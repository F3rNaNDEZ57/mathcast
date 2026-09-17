import ipv4_first  # noqa: F401  - IPv6 is black-holed here; see the module docstring

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class TestScene(VoiceoverScene):
    def construct(self):
        # Initialize the Google TTS engine (no local models needed)
        self.set_speech_service(GTTSService())

        # Basic text test
        text = Text("Welcome to the automated pipeline.", font_size=48)
        
        with self.voiceover(text="Welcome to the automated pipeline. This is a Google TTS test.") as tracker:
            self.play(Write(text), run_time=tracker.duration)
            
        self.wait(1)
        
        # Mathematical equation test
        equation = MathTex(r"e^{i\pi} + 1 = 0", font_size=72)
        equation.next_to(text, DOWN, buff=1.0)
        
        with self.voiceover(text="Here we see Euler's identity rendered perfectly using Math TeX.") as tracker:
            self.play(TransformFromCopy(text, equation), run_time=tracker.duration)
            
        self.wait(2)
        
        self.play(FadeOut(text), FadeOut(equation))
