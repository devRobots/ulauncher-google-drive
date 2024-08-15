from src.drive import Drive

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction


class DriveExtension(Extension):
	def __init__(self):
		super().__init__()
		self.subscribe(KeywordQueryEvent, DriveEventListener(Drive()))


class DriveEventListener(EventListener):
	def __init__(self, drive):
		self.drive = drive

	def get_icon(self, mime_type):
		if "folder" in mime_type:
			return "images/files/folder.png"
		if "text" in mime_type or "pdf" in mime_type or "document" in mime_type:
			return "images/files/text.png"
		if "image" in mime_type:
			return "images/files/image.png"
		if "audio" in mime_type:
			return "images/files/audio.png"
		if "video" in mime_type:
			return "images/files/video.png"
		return "images/files/app.png"

	def sizeof_fmt(self, num, suffix="B"):
		for unit in ("", "K", "M", "G", "T"):
			if abs(num) < 1024:
				return f"{num:3.1f}{unit}{suffix}"
			num /= 1024
		return f"{num:.1f}Yi{suffix}"


	def on_event(self, event, extension):
		query = event.get_argument()

		if not query or len(query.strip()) < 2:
			return RenderResultListAction(
				[
      		ExtensionResultItem(
						icon="images/icon.png",
						name="Search Google Drive",
						description="Type the name of the file you are looking for",
						on_enter=HideWindowAction(),
					)
        ]
			)

		items = []
		files = self.drive.search_files(query)
		files = files if len(files) <= 5 else files[:5]

		for file in files:
			icon = self.get_icon(file.get("mimeType"))
			name = file.get("name")
			link = file.get("webViewLink")

			size_raw = file.get("size")
			size = self.sizeof_fmt(float(size_raw)) if size_raw else "0B"
			owner = file.get("owners")[0].get("displayName")
			create_time = file.get("createdTime").split(".")[0]
   
			description = f"{size} by: {owner} at: {create_time}"

			item = ExtensionResultItem(
				icon=icon,
				name=name,
				description="Open in browser" if not size_raw else description,
				on_enter=OpenUrlAction(link),
			)
			items.append(item)

		return RenderResultListAction(items)


if __name__ == "__main__":
	DriveExtension().run()
