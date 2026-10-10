extends RefCounted
## Display settings, applied from code on every launch (title.gd calls apply() first thing).
## project.godot holds the same values, but an installed game that updated itself through game.pck
## keeps the project settings of the build it was installed from: Godot reads them once, from the
## exe. Without this, a v0.1.0 install showed every label in Godot's default 16px font. Keep it in
## step with project.godot.

const THEME := preload("res://theme.tres")


static func apply(tree: SceneTree) -> void:
	var root := tree.root
	# render on the 320x180 grid, scaled up by whole numbers (display/window/stretch/*)
	root.content_scale_size = Vector2i(320, 180)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
	root.content_scale_stretch = Window.CONTENT_SCALE_STRETCH_INTEGER
	root.snap_2d_transforms_to_pixel = true
	root.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	# the pixel font for every Control without its own (gui/theme/custom). Our labels live under
	# Node2D scenes, which don't pass a Window's theme down, so set it where they all fall back to.
	var fallback := ThemeDB.get_default_theme()
	fallback.default_font = THEME.default_font
	fallback.default_font_size = THEME.default_font_size
