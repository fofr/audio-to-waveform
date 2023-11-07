import subprocess
from cog import BasePredictor, Input, Path
import gradio as gr
import tempfile

class Predictor(BasePredictor):
    def predict(self,
        audio: Path = Input(description="Audio file to create waveform from"),
        bg_color: str = Input(description="Background color of waveform", default="#000000"),
        fg_alpha: float = Input(description="Opacity of foreground waveform", default=0.75),
        bars_color: str = Input(description="Color of waveform bars", default="#ffffff"),
        bar_count: int = Input(description="Number of bars in waveform", default=100),
        bar_width: float = Input(description="Width of bars in waveform. 1 represents full width, 0.5 represents half width, etc.", default=0.4),
        caption_text: str = Input(description="Caption text for the video", default=""),
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
            return Path(waveform_video)
        else:
            padded_waveform_path = tempfile.mktemp(suffix=".mp4")
            background_image_path = tempfile.mktemp(suffix=".png")
            final_video_path = tempfile.mktemp(suffix=".mp4")

            # Add padding to the top of the waveform video
            subprocess.run([
                'ffmpeg', '-y', '-i', waveform_video, '-vf',
                f'pad=width=1000:height=667:x=0:y=267:color={bg_color[1:]}',
                padded_waveform_path
            ], check=True)

            # Create an image using ImageMagick
            subprocess.run([
                'convert', '-background', 'transparent', '-fill', bars_color, '-font', 'font/Roboto-Black.ttf',
                '-pointsize', '48', '-size', '900x267', '-gravity', 'center', f'caption:{caption_text}',
                '-bordercolor', 'transparent', '-border', '10', background_image_path
            ], check=True)

            # Overlay the image on the padded waveform video
            subprocess.run([
                'ffmpeg', '-y', '-i', padded_waveform_path, '-i', background_image_path,
                '-filter_complex', 'overlay=0:0', final_video_path
            ], check=True)

        return Path(final_video_path)
