from pathlib import Path
from types import SimpleNamespace
import importlib.util

rnd_str_prvdr = "random_string_provider.py"
tmp_stmp_prvdr = "timestamp_provider.py"
TARGET_IMAGE_SIZE = 350
HEADROOM_IMAGE_SIZE = 150
MASK_A_SATURATION = 0
MASK_A_BRIGHTNESS = -127
MASK_A_CONTRAST = -127
MASK_B_BRIGHTNESS = -127
MASK_B_CONTRAST = 127
GIMP_BRIGHTNESS_CONTRAST_MAX_VALUE = 127
TRACE_BITMAP_THRESHOLD = 0.450
TRACE_BITMAP_INVERT = False
TRACE_BITMAP_SPECKLES = 2
TRACE_BITMAP_SMOOTH_CORNERS = 1.00
TRACE_BITMAP_OPTIMIZE = 0.200
TRACE_BITMAP_SELECT_AREA = False
TRACE_BITMAP_COLOR_SCANS = 2
TRACE_BITMAP_SMOOTH = False
TRACE_BITMAP_STACK = False
TRACE_BITMAP_REMOVE_BACKGROUND = False
LAYER2_RADIAL_GRADIENT_RADIUS = 3
SVG_OBJECT_OPACITY = 1.0
SVG_BLUR_PERCENT = 40.0
FINAL_VERSION2_OPACITY = 0.50
FINAL_MASK_OVERLAY_OPACITY = 0.65
FINAL_MASK_OVERLAY_BLUR_PERCENT = 0
manufacturer_name = None
product_family = None
product_name = None
loc_db = None
inkscape_executable_path = None
gimp_executable_path = None
gimp_tool_key = None
source_images_path = None
scaled_images_path = None
step_one_pngs = None
step_two_pngs = None
qfying_pngs = None
masks_svg_path = None
final_path = None
gimp_batch_profile_path = None
manufacture_database = None
graphic_items_database = None


def create_runtime():
    return SimpleNamespace(
        rnd_str_prvdr=rnd_str_prvdr,
        tmp_stmp_prvdr=tmp_stmp_prvdr,
        TARGET_IMAGE_SIZE=TARGET_IMAGE_SIZE,
        HEADROOM_IMAGE_SIZE=HEADROOM_IMAGE_SIZE,
        MASK_A_SATURATION=MASK_A_SATURATION,
        MASK_A_BRIGHTNESS=MASK_A_BRIGHTNESS,
        MASK_A_CONTRAST=MASK_A_CONTRAST,
        MASK_B_BRIGHTNESS=MASK_B_BRIGHTNESS,
        MASK_B_CONTRAST=MASK_B_CONTRAST,
        GIMP_BRIGHTNESS_CONTRAST_MAX_VALUE=GIMP_BRIGHTNESS_CONTRAST_MAX_VALUE,
        TRACE_BITMAP_THRESHOLD=TRACE_BITMAP_THRESHOLD,
        TRACE_BITMAP_INVERT=TRACE_BITMAP_INVERT,
        TRACE_BITMAP_SPECKLES=TRACE_BITMAP_SPECKLES,
        TRACE_BITMAP_SMOOTH_CORNERS=TRACE_BITMAP_SMOOTH_CORNERS,
        TRACE_BITMAP_OPTIMIZE=TRACE_BITMAP_OPTIMIZE,
        TRACE_BITMAP_SELECT_AREA=TRACE_BITMAP_SELECT_AREA,
        TRACE_BITMAP_COLOR_SCANS=TRACE_BITMAP_COLOR_SCANS,
        TRACE_BITMAP_SMOOTH=TRACE_BITMAP_SMOOTH,
        TRACE_BITMAP_STACK=TRACE_BITMAP_STACK,
        TRACE_BITMAP_REMOVE_BACKGROUND=TRACE_BITMAP_REMOVE_BACKGROUND,
        LAYER2_RADIAL_GRADIENT_RADIUS=LAYER2_RADIAL_GRADIENT_RADIUS,
        SVG_OBJECT_OPACITY=SVG_OBJECT_OPACITY,
        SVG_BLUR_PERCENT=SVG_BLUR_PERCENT,
        FINAL_VERSION2_OPACITY=FINAL_VERSION2_OPACITY,
        FINAL_MASK_OVERLAY_OPACITY=FINAL_MASK_OVERLAY_OPACITY,
        FINAL_MASK_OVERLAY_BLUR_PERCENT=FINAL_MASK_OVERLAY_BLUR_PERCENT,
        manufacturer_name=manufacturer_name,
        product_family=product_family,
        product_name=product_name,
        loc_db=loc_db,
        inkscape_executable_path=inkscape_executable_path,
        gimp_executable_path=gimp_executable_path,
        gimp_tool_key=gimp_tool_key,
        source_images_path=source_images_path,
        scaled_images_path=scaled_images_path,
        step_one_pngs=step_one_pngs,
        step_two_pngs=step_two_pngs,
        qfying_pngs=qfying_pngs,
        masks_svg_path=masks_svg_path,
        final_path=final_path,
        gimp_batch_profile_path=gimp_batch_profile_path,
        manufacture_database=manufacture_database,
        graphic_items_database=graphic_items_database,
    )


def load_pipeline():
    script_path = Path(__file__).resolve()
    pipeline_path = script_path.parent / "subscripts" / "graphic_items_bulder_pipeline.py"
    spec = importlib.util.spec_from_file_location(
        "graphic_items_bulder_pipeline",
        pipeline_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Pipeline konnte nicht geladen werden: {pipeline_path}")
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    return pipeline


def run():
    runtime = create_runtime()
    pipeline = load_pipeline()
    pipeline.load(runtime)
    runtime.main(runtime, Path(__file__).resolve())


if __name__ == "__main__":
    run()
