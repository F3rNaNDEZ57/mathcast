from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class Chapter2Neuron(VoiceoverScene):
    def construct(self):
        # Initialize the speech service
        self.set_speech_service(GTTSService())

        # ---------------------------------------------------------------------
        # Part 1: Biological vs. Artificial Neuron Mapping
        # ---------------------------------------------------------------------
        with self.voiceover(text="To understand artificial neural networks, we must first examine the mapping between biological and artificial neurons.") as tracker:
            header = Text("Biological vs. Artificial Neuron")
            header.to_edge(UP)
            
            comparison_data = [
                ["Biological", "Artificial"],
                ["Dendrites", "Inputs"],
                ["Synapses", "Weights"],
                ["Soma", "Summation"],
                ["Axon", "Activation/Output"]
            ]
            comparison_table = Table(
                comparison_data,
                include_outer_lines=True
            ).scale(0.6).next_to(header, DOWN)
            
            self.play(Write(header), run_time=tracker.duration * 0.3)
            self.play(Create(comparison_table), run_time=tracker.duration * 0.7)

        with self.voiceover(text="Visually, the artificial neuron takes multiple inputs, multiplies them by weights, and sums them within a core.") as tracker:
            self.play(FadeOut(comparison_table))
            
            # Diagram elements
            neuron_core = Circle(radius=1.0, color=WHITE).shift(RIGHT * 2)
            core_label = MathTex(r"\sum, f").move_to(neuron_core.get_center())
            
            inputs = VGroup(
                MathTex(r"x_1"),
                MathTex(r"x_2"),
                MathTex(r"x_m")
            ).arrange(DOWN, buff=1.0).to_edge(LEFT, buff=1.5)
            
            arrows = VGroup()
            weights = VGroup()
            for i, input_obj in enumerate(inputs):
                arrow = Arrow(input_obj.get_right(), neuron_core.get_left(), buff=0.1)
                weight = MathTex(fr"w_{i+1 if i < 2 else 'm'}").next_to(arrow, UP, buff=0.1)
                arrows.add(arrow)
                weights.add(weight)
                
            output_arrow = Arrow(neuron_core.get_right(), neuron_core.get_right() + RIGHT * 1.5)
            output_label = MathTex(r"y").next_to(output_arrow, RIGHT)

            self.play(
                Create(neuron_core),
                Write(core_label),
                Write(inputs),
                Create(arrows),
                Write(weights),
                Create(output_arrow),
                Write(output_label),
                run_time=tracker.duration
            )

        self.play(FadeOut(*self.mobjects))

        # ---------------------------------------------------------------------
        # Part 2: Core Mathematics and Induced Local Field
        # ---------------------------------------------------------------------
        with self.voiceover(text="The core computation results in the induced local field, denoted as z. It is the weighted sum of inputs plus a bias term.") as tracker:
            induced_field = MathTex(
                r"z", r"=", r"\sum_{i=1}^{m} w_i x_i", r"+", r"b", r"=", r"\mathbf{w}^\top \mathbf{x} + b"
            )
            induced_field.set_color_by_tex("b", YELLOW)
            self.play(Write(induced_field), run_time=tracker.duration)

        with self.voiceover(text="The bias, highlighted here in yellow, is crucial because it shifts the decision function along the input space.") as tracker:
            bias_explanation = Text("Bias shifts the decision function", font_size=24, color=YELLOW)
            bias_explanation.next_to(induced_field, DOWN, buff=0.5)
            self.play(Write(bias_explanation), run_time=tracker.duration)

        self.play(FadeOut(*self.mobjects))

        # ---------------------------------------------------------------------
        # Part 3: Activation Functions
        # ---------------------------------------------------------------------
        with self.voiceover(text="Once z is calculated, an activation function determines the output. First, the Threshold function outputs one if z is non-negative, and zero otherwise.") as tracker:
            threshold_eq = MathTex(
                r"f(z) = \begin{cases} 1 & \text{if } z \geq 0 \\ 0 & \text{if } z < 0 \end{cases}"
            ).to_edge(UP, buff=1.0)
            self.play(Write(threshold_eq), run_time=tracker.duration)

        with self.voiceover(text="Second, the Sigmoid function maps the input to a continuous range between zero and one, useful for probabilities.") as tracker:
            sigmoid_eq = MathTex(
                r"\sigma(z) = \frac{1}{1 + e^{-z}}"
            ).next_to(threshold_eq, DOWN, buff=0.5)
            self.play(Write(sigmoid_eq), run_time=tracker.duration)

        with self.voiceover(text="Finally, the ReLU function, or Rectified Linear Unit, simply outputs the maximum of zero and z.") as tracker:
            relu_eq = MathTex(
                r"\text{ReLU}(z) = \max(0, z)"
            ).next_to(sigmoid_eq, DOWN, buff=0.5)
            self.play(Write(relu_eq), run_time=tracker.duration)

        self.play(FadeOut(*self.mobjects))

        # ---------------------------------------------------------------------
        # Part 4: The Perceptron Update Rule
        # ---------------------------------------------------------------------
        with self.voiceover(text="To learn, the perceptron updates its weights using the error between the desired output d and the actual output y.") as tracker:
            update_rule = MathTex(
                r"\mathbf{w}(n+1) = \mathbf{w}(n) + \eta [d(n) - y(n)] \mathbf{x}(n)"
            )
            error_note = Text("Error component: d(n) - y(n)", font_size=24).next_to(update_rule, DOWN, buff=0.5)
            
            self.play(Write(update_rule), run_time=tracker.duration * 0.7)
            self.play(Write(error_note), run_time=tracker.duration * 0.3)

        self.play(FadeOut(*self.mobjects))

        # ---------------------------------------------------------------------
        # Part 5: Worked Example
        # ---------------------------------------------------------------------
        with self.voiceover(text="Let's look at a worked example. Given the equation z equals 2 x-one minus x-two plus 0.5.") as tracker:
            ex_eq = MathTex(r"z = 2x_1 - x_2 + 0.5").to_edge(UP)
            self.play(Write(ex_eq), run_time=tracker.duration)

        with self.voiceover(text="Substituting x-one equals 1 and x-two equals 3, the value of z becomes 2 times 1, minus 3, plus 0.5, which equals negative 0.5.") as tracker:
            ex_sub = MathTex(r"z = 2(1) - (3) + 0.5 = -0.5").next_to(ex_eq, DOWN)
            self.play(Write(ex_sub), run_time=tracker.duration)

        with self.voiceover(text="Applying the Threshold function to negative 0.5 results in 0, as the value is less than zero.") as tracker:
            res_threshold = MathTex(r"f(-0.5) = 0").next_to(ex_sub, DOWN, buff=0.5).set_color(RED)
            self.play(Write(res_threshold), run_time=tracker.duration)

        with self.voiceover(text="Applying the Sigmoid function, the result is approximately 0.3775.") as tracker:
            res_sigmoid = MathTex(r"\sigma(-0.5) \approx 0.3775").next_to(res_threshold, DOWN).set_color(BLUE)
            self.play(Write(res_sigmoid), run_time=tracker.duration)

        self.play(FadeOut(*self.mobjects))
        self.wait(2)