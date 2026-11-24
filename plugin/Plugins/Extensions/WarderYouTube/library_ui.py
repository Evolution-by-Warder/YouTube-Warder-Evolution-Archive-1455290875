# -*- coding: utf-8 -*-
"""Native Enigma2 Favourites / History browser; no external renderers.

The receiver's TV service stays running while browsing, as requested by the
owner. Only playback activates the existing native Warder MoviePlayer.
"""
from .header_ui import add_header
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from .menu_compat import selected_index
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from twisted.internet.threads import deferToThread

from .skin import LIBRARY_SKIN
from .local_library import (
    LibraryError, list_videos, remove_video, clear_videos,
    toggle_favourite, record_opened
)
from .resolver import ResolverError, resolve_video_streams
from .settings import get_quality, get_api_key
from .video_metadata import fetch_video_info
from .video_info_display import format_video_info
from .i18n import tr as _
from .data_auth import can_use_data_api, account_available
from .confirm_ui import WarderYouTubeConfirm
from .info_ui import WarderYouTubeInfo


class WarderYouTubeLibrary(Screen):
    skin = LIBRARY_SKIN

    def __init__(self, session, kind):
        if kind not in ("favourites", "history", "youtube_likes"):
            raise ValueError("Unknown video library")
        Screen.__init__(self, session)
        add_header(self)
        self.kind = kind
        self.video_items = []
        self.busy = False
        self.playback_active = False
        self.disposed = False
        self.confirmation_open = False
        self.request_version = 0
        self.likes_page_token = ""
        self.likes_previous_tokens = []
        self.likes_next_token = ""
        self.likes_loaded = False
        self.favourites_sync_busy = False
        self.favourites_sync_started = False
        self.favourites_sync_epoch = 0

        title = (_("Páči sa mi na YouTube") if kind == "youtube_likes"
                 else _("Favourites") if kind == "favourites" else _("History"))
        self["title"] = Label("YouTube Warder Evolution / " + title)
        self["subtitle"] = Label("")
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Play video"))
        self["key_yellow"] = Label(
            _("Predchádzajúca strana") if kind == "youtube_likes"
            else _("Remove video from favourites") if kind == "favourites"
            else _("Delete video from history")
        )
        self["key_blue"] = Label(
            _("Ďalšia strana") if kind == "youtube_likes"
            else _("Clear all favourite videos") if kind == "favourites"
            else _("Clear entire history")
        )
        self["results"] = MenuList([])
        self["status"] = Label("")
        self["footer"] = Label(
            _("OK: prehrať · MENU: akcie · ŽLTÉ: späť · MODRÉ: ďalšia strana · EXIT: obľúbené")
            if kind == "youtube_likes" else
            _("OK: play · INFO: details · MENU: actions · YELLOW: remove favourite · BLUE: clear favourites · EXIT: home")
            if kind == "favourites" else
            _("OK: play · INFO: details · MENU: actions · YELLOW: delete from history · BLUE: clear history · EXIT: home")
        )
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "InfoActions", "MenuActions"],
            {
                "ok": self.play_selected, "info": self.show_info,
                "menu": self.open_actions, "green": self.play_selected,
                "yellow": self.previous_likes_page if kind == "youtube_likes" else self.remove_selected,
                "blue": self.next_likes_page if kind == "youtube_likes" else self.confirm_clear,
                "cancel": self.close,
                "red": self.close
            }, -1
        )
        self["results"].onSelectionChanged.append(self.selection_changed)
        self.onShown.append(self.on_show)
        self.onClose.append(self.dispose)

    def dispose(self):
        self.disposed = True
        self.request_version += 1
        self.favourites_sync_epoch += 1

    def on_show(self):
        """Keep local videos immediately visible; merge missing likes in a worker."""
        self.refresh()
        if self.kind == "favourites":
            self.start_favourites_sync()

    def start_favourites_sync(self):
        if (self.disposed or self.kind != "favourites"
                or self.favourites_sync_busy or self.favourites_sync_started
                or self.playback_active):
            return
        from .video_ratings import can_like
        if not can_like():
            return  # Signed out/read-only accounts keep their local list.
        from .favourites_sync import sync_youtube_favourites
        self.favourites_sync_started = True
        self.favourites_sync_busy = True
        self.favourites_sync_epoch += 1
        epoch = self.favourites_sync_epoch
        self["status"].setText(_("Kontrolujem nové obľúbené z YouTube…"))
        try:
            task = deferToThread(sync_youtube_favourites)
            task.addCallbacks(
                lambda result: self.favourites_sync_ready(epoch, result),
                lambda error: self.favourites_sync_failed(epoch, error))
        except Exception:
            self.favourites_sync_failed(epoch, None)

    def favourites_sync_ready(self, epoch, result):
        if self.disposed or epoch != self.favourites_sync_epoch:
            return
        self.favourites_sync_busy = False
        if not isinstance(result, dict):
            return self.favourites_sync_failed(epoch, None)
        added = result.get("added", 0)
        if not isinstance(added, int) or added < 0:
            return self.favourites_sync_failed(epoch, None)
        # Refresh reads the atomically updated local file, preserving native
        # selection and avoiding any account-only network calls in the GUI.
        if added:
            selection = selected_index(self["results"])
            self.refresh()
            try:
                self["results"].moveToIndex(min(selection, len(self.video_items) - 1))
            except (AttributeError, ValueError, TypeError):
                pass
        message = (_("Do Obľúbených bolo doplnených %d videí z YouTube.") % added
                   if added else _("Obľúbené sú aktuálne."))
        if result.get("truncated") or result.get("capacity_reached"):
            message += " " + _("Dosiahnutý limit importu; lokálne videá zostali zachované.")
        self["status"].setText(message)

    def favourites_sync_failed(self, epoch, failure):
        if self.disposed or epoch != self.favourites_sync_epoch:
            return
        self.favourites_sync_busy = False
        error = getattr(failure, "value", failure)
        from .video_ratings import VideoRatingError
        self["status"].setText(
            str(error) if isinstance(error, (LibraryError, VideoRatingError))
            else _("YouTube Obľúbené sa teraz nepodarilo doplniť; miestne videá zostali zachované.")
        )

    def refresh(self):
        if self.disposed or self.busy or self.playback_active:
            return
        if self.kind == "youtube_likes":
            if not self.likes_loaded:
                self.request_likes_page()
            return
        try:
            items = list_videos(self.kind)
        except LibraryError as error:
            self.video_items = []
            self["results"].setList([])
            self["status"].setText(str(error))
            return
        self.video_items = items
        self["results"].setList([
            "%s   |   %s" % ((item["title"] or "YouTube video")[:93],
                             item["channel"][:50])
            for item in items
        ])
        self["subtitle"].setText("%s: %d videí" % (
            _("Favourites") if self.kind == "favourites" else _("Recently opened"), len(items)))
        self["status"].setText(
            _("Zoznam je prázdny. V hľadaní stlač MENU na uloženie videa.")
            if not items and self.kind == "favourites" else
            _("História je prázdna. Otvor video z výsledkov hľadania.")
            if not items else _("Vyber video a stlač OK. Prehrávanie nepotrebuje API kľúč.")
        )


    def request_likes_page(self):
        """Read account likes in a worker, never on the Enigma2 GUI thread."""
        if (self.kind != "youtube_likes" or self.disposed
                or self.busy or self.playback_active):
            return
        from .video_ratings import liked_videos_page
        self.busy = True
        self.request_version += 1
        version = self.request_version
        self["status"].setText(_("Načítavam videá Páči sa mi z YouTube…"))
        try:
            task = deferToThread(liked_videos_page, self.likes_page_token)
            task.addCallbacks(lambda payload: self.likes_ready(version, payload),
                              lambda err: self.likes_failed(version, err))
        except Exception:
            self.likes_failed(version, None)

    def likes_ready(self, version, payload):
        if self.disposed or version != self.request_version:
            return
        self.busy = False
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            return self.likes_failed(version, None)
        self.video_items = list(payload["items"])
        self.likes_next_token = payload.get("next_page_token") or ""
        self.likes_loaded = True
        self["results"].setList([
            "%s   |   %s" % ((item["title"] or "YouTube video")[:93],
                           (item["channel"] or "")[:50])
            for item in self.video_items
        ])
        self["subtitle"].setText(_("Páči sa mi na YouTube") +
                                 ": %d   ·   %d videí" % (
                                     len(self.likes_previous_tokens) + 1,
                                     len(self.video_items)))
        self["status"].setText(
            _("Žiadne hodnotené videá na tejto stránke.")
            if not self.video_items else
            _("OK: prehrať · MENU: akcie · MODRÉ: ďalšia strana")
        )

    def likes_failed(self, version, failure):
        if self.disposed or version != self.request_version:
            return
        self.busy = False
        error = getattr(failure, "value", failure)
        from .video_ratings import VideoRatingError
        self["status"].setText(
            str(error) if isinstance(error, VideoRatingError)
            else _("Nepodarilo sa načítať Páči sa mi z YouTube.")
        )

    def next_likes_page(self):
        if (self.kind != "youtube_likes" or self.busy or self.disposed
                or not self.likes_next_token):
            return
        self.likes_previous_tokens.append(self.likes_page_token)
        self.likes_page_token = self.likes_next_token
        self.likes_loaded = False
        self.request_likes_page()

    def previous_likes_page(self):
        if (self.kind != "youtube_likes" or self.busy or self.disposed
                or not self.likes_previous_tokens):
            return
        self.likes_page_token = self.likes_previous_tokens.pop()
        self.likes_loaded = False
        self.request_likes_page()

    def like_selected(self):
        if self.disposed or self.busy or self.playback_active:
            return
        item = self._selected()
        if item is None:
            return
        from .video_ratings import like_video
        self.busy = True
        self.request_version += 1
        version = self.request_version
        self["status"].setText(_("Odosielam Páči sa mi na YouTube…"))
        try:
            task = deferToThread(like_video, item["video_id"])
            task.addCallbacks(lambda saved: self.like_ready(version, saved),
                              lambda err: self.like_failed(version, err))
        except Exception:
            self.like_failed(version, None)

    def like_ready(self, version, saved):
        if self.disposed or version != self.request_version:
            return
        self.busy = False
        self["status"].setText(
            _("Video označené Páči sa mi na YouTube.")
            if saved is True else _("YouTube nepotvrdil hodnotenie videa.")
        )

    def like_failed(self, version, failure):
        if self.disposed or version != self.request_version:
            return
        self.busy = False
        error = getattr(failure, "value", failure)
        from .video_ratings import VideoRatingError
        self["status"].setText(
            str(error) if isinstance(error, VideoRatingError)
            else _("Nepodarilo sa označiť Páči sa mi.")
        )

    def _selected(self):
        if self.disposed:
            return None
        index = selected_index(self["results"])
        if 0 <= index < len(self.video_items):
            return self.video_items[index]
        return None

    def selection_changed(self):
        # No network requests when browsing locally stored video names.
        return

    def show_info(self):
        if self.disposed or self.busy or self.playback_active or self.confirmation_open:
            return
        item = self._selected()
        if item is None:
            return
        key = get_api_key()
        if not can_use_data_api(key):
            self.session.open(
                WarderYouTubeInfo,
                format_video_info(
                    item, translate=_,
                    note="Sign in to YouTube for detailed video information. A personal API key is optional."
                ), video=item
            )
            return
        # INFO is the only point where metadata is requested. Never fetch
        # while browsing names; ignore callbacks after the screen closes.
        self.busy = True
        self.request_version += 1
        token = self.request_version
        self["status"].setText(_("Loading video details…"))
        try:
            worker = deferToThread(fetch_video_info, item["video_id"], key)
            worker.addCallbacks(
                lambda details: self.info_ready(token, item, details),
                lambda failure: self.info_failed(token, item, failure)
            )
        except Exception:
            self.info_failed(token, item, None)

    def info_ready(self, token, item, details):
        if self.disposed or token != self.request_version:
            return
        self.busy = False
        self["status"].setText(_("Video details loaded."))
        self.session.open(
            WarderYouTubeInfo,
            format_video_info(item, details, translate=_), video=item
        )

    def info_failed(self, token, item, failure):
        if self.disposed or token != self.request_version:
            return
        self.busy = False
        self["status"].setText(_("Details unavailable; showing saved video information."))
        self.session.open(
            WarderYouTubeInfo,
            format_video_info(
                item, translate=_,
                note="Details unavailable; showing saved video information."
            ), video=item
        )

    def open_actions(self):
        item = self._selected()
        if item is None or self.busy or self.playback_active:
            return
        from .context_menu import WarderYouTubeContext
        try:
            saved = any(x["video_id"] == item["video_id"]
                        for x in list_videos("favourites"))
        except LibraryError:
            saved = False
        self.session.openWithCallback(
            self.action_selected, WarderYouTubeContext, item,
            saved, self.kind)

    def action_selected(self, action):
        if self.disposed:
            return
        if action == "play":
            self.play_selected()
        elif action == "favorite":
            self.save_favourite()
        elif action == "like_youtube":
            self.like_selected()
        elif action == "youtube_likes":
            self.session.open(WarderYouTubeLibrary, "youtube_likes")
        elif action == "info":
            self.show_info()
        elif action == "remove":
            self.remove_selected()
        elif action == "clear":
            self.confirm_clear()

    def save_favourite(self):
        if self.busy or self.playback_active:
            return
        item = self._selected()
        if item is None:
            return
        try:
            added = toggle_favourite(item)
            if self.kind == "favourites":
                self.refresh()
            self["status"].setText(
                "Video pridané do obľúbených." if added
                else "Video odstránené z obľúbených."
            )
        except LibraryError as error:
            self["status"].setText(str(error))

    def remove_selected(self):
        if self.kind == "youtube_likes" or self.busy or self.playback_active:
            return
        item = self._selected()
        if item is None:
            return
        try:
            removed = remove_video(self.kind, item["video_id"])
            self.refresh()
            if removed:
                self["status"].setText(
                    _("Video removed from favourites.") if self.kind == "favourites"
                    else _("Video removed from history.")
                )
        except LibraryError as error:
            self["status"].setText(str(error))

    def confirm_clear(self):
        if self.kind == "youtube_likes":
            return
        if (self.disposed or self.busy or self.playback_active
                or self.confirmation_open or not self.video_items):
            return
        self.confirmation_open = True
        try:
            self.session.openWithCallback(
                self.clear_confirmed, WarderYouTubeConfirm,
                (_("Clear all favourite videos") if self.kind == "favourites"
                 else _("Clear entire history")) + "?"
            )
        except Exception:
            self.confirmation_open = False
            self["status"].setText("Potvrdenie nebolo možné zobraziť.")

    def clear_confirmed(self, confirmed):
        self.confirmation_open = False
        if self.disposed or not confirmed or self.kind == "youtube_likes":
            return
        try:
            clear_videos(self.kind)
            self.refresh()
            self["status"].setText(
                _("All favourite videos removed.") if self.kind == "favourites"
                else _("Entire history cleared.")
            )
        except LibraryError as error:
            self["status"].setText(str(error))

    def play_selected(self):
        if self.busy or self.playback_active or self.disposed or self.confirmation_open:
            return
        item = self._selected()
        if item is None:
            return
        self.busy = True
        self.request_version += 1
        version = self.request_version
        self["status"].setText("Hľadám kompatibilný YouTube stream...")
        try:
            from .player import dash_available
            deferred = deferToThread(
                resolve_video_streams, item["video_id"],
                quality=get_quality(), dash=dash_available()
            )
            deferred.addCallbacks(
                lambda streams: self.play_ready(version, item, streams),
                lambda error: self.play_error(version, error)
            )
        except Exception:
            self.busy = False
            self["status"].setText("Prehrávanie sa nepodarilo spustiť.")

    def play_ready(self, version, item, streams):
        if self.disposed or version != self.request_version:
            return
        self.busy = False
        if self.playback_active:
            return
        self.playback_active = True
        self["status"].setText("Otváram prehrávač Enigma2...")
        try:
            from .player import open_player
            open_player(self.session, streams, item["title"],
                        on_close=self.player_closed)
        except Exception:
            self.playback_active = False
            self["status"].setText("Prehrávač Enigma2 sa nepodarilo otvoriť.")
            return
        try:
            record_opened(item)
        except LibraryError:
            # Saving history never takes precedence over playback.
            pass

    def play_error(self, version, failure):
        if self.disposed or version != self.request_version:
            return
        self.busy = False
        error = getattr(failure, "value", None)
        self["status"].setText(
            str(error) if isinstance(error, ResolverError)
            else "Kompatibilný stream sa nepodarilo získať."
        )

    def player_closed(self, failed=False, *args):
        self.playback_active = False
        if self.disposed:
            return
        self.refresh()
        self["status"].setText(
            "Video sa nepodarilo prehrať. Skús iné video alebo kvalitu 360p."
            if failed is True else "Prehrávanie ukončené. OK: ďalšie video."
        )
