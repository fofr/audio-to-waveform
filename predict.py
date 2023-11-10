import subprocess
from cog import BasePredictor, Input, Path
import gradio as gr
import tempfile


class Predictor(BasePredictor):
    def predict(
        self,
        audio: Path = Input(description="Audio file to create waveform from"),
        caption_text: str = Input(description="Caption text for the video", default=""),
        bg_color: str = Input(
            description="Background color of waveform", default="#000000"
        ),
        fg_alpha: float = Input(
            description="Opacity of foreground waveform", default=0.75
        ),
        bars_color: str = Input(
            description="Color of waveform bars", default="#ffffff"
        ),
        bar_count: int = Input(description="Number of bars in waveform", default=100),
        bar_width: float = Input(
            description="Width of bars in waveform. 1 represents full width, 0.5 represents half width, etc.",
            default=0.4,
        ),
        width: int = Input(description="Video width", default=1000),
        waveform_height: int = Input(description="Height of the waveform", default=200),
        caption_height: int = Input(description="Height of the caption text box", default=150),
        caption_left_right_padding: int = Input(
            description="Padding to the left and right of the caption text", default=50
        ),
        caption_top_padding: int = Input(
            description="Padding to the top of the caption text", default=10
        ),
    ) -> Path:
        """Make waveform video from audio file"""
        waveform_video = gr.make_waveform(
            str(audio),
            bg_color=bg_color,
            fg_alpha=fg_alpha,
            bars_color=bars_color,
            bar_count=bar_count,
            bar_width=bar_width,
        )

        if caption_text == "" or caption_text is None:
            scaled_waveform_path = tempfile.mktemp(suffix=".mp4")
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    waveform_video,
                    "-vf",
                    f"scale={width}:{waveform_height}:flags=neighbor",
                    "-c:a",
                    "copy",
                    scaled_waveform_path,
                ],
                check=True,
            )

            return Path(scaled_waveform_path)
        else:
            total_height = waveform_height + caption_height
            padded_waveform_path = tempfile.mktemp(suffix=".mp4")
            caption_width = width - (caption_left_right_padding * 2)

            background_image_path = tempfile.mktemp(suffix=".png")
            final_video_path = tempfile.mktemp(suffix=".mp4")

            # Add padding to the top of the waveform video
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    waveform_video,
                    "-vf",
                    f"scale={width}:{waveform_height}:flags=neighbor,pad=width={width}:height={total_height}:x=0:y={caption_height}:color={bg_color[1:]}",
                    "-c:a",
                    "copy",
                    padded_waveform_path,
                ],
                check=True,
            )

            # Create an image using ImageMagick
            subprocess.run(
                [
                    "convert",
                    "-background",
                    "transparent",
                    "-fill",
                    bars_color,
                    "-font",
                    "font/Roboto-Black.ttf",
                    "-pointsize",
                    "48",
                    "-size",
                    f"{caption_width}x{caption_height}",
                    "-gravity",
                    "center",
                    f"caption:{caption_text}",
                    "-bordercolor",
                    "transparent",
                    "-border",
                    f"{caption_top_padding}",
                    background_image_path,
                ],
                check=True,
            )

            # Overlay the image on the padded waveform video
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    padded_waveform_path,
                    "-i",
                    background_image_path,
                    "-filter_complex",
                    "overlay=0:0",
                    final_video_path,
                ],
                check=True,
            )

        return Path(final_video_path)
