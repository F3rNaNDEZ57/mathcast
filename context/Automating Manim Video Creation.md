# Architecting an Autonomous Generative Pipeline for Educational Mathematical Animation Using Gemini CLI, Local Text-to-Speech, and Manim

## 1. Introduction to the Paradigm of Automated Programmatic Animation

The creation of high-fidelity, mathematically rigorous educational animations has historically presented a significant bottleneck in the dissemination of technical knowledge. Producing visual explanations of complex concepts, such as artificial neural networks and perceptron learning paradigms, requires a synthesis of disparate, highly specialized skills. An educational creator must possess a deep understanding of the mathematical domain, proficiency in vector graphics or programmatic animation frameworks, expertise in audio engineering for voiceover synchronization, and the editorial capability to merge these streams into a cohesive pedagogical narrative. The advent of large language models (LLMs) equipped with advanced coding capabilities, coupled with localized neural text-to-speech (TTS) engines and programmatic animation libraries like Manim (Mathematical Animation Engine), introduces a profound paradigm shift.1

This research report exhaustively details the architecture, engineering, and deployment of a fully automated, end-to-end generative pipeline. This pipeline is designed to ingest a raw educational text file—specifically, a markdown document detailing the biological versus artificial neuron and the perceptron learning rule—and autonomously synthesize a 1080p, voice-narrated mathematical animation. The orchestration of this pipeline relies on the Google Gemini Command Line Interface (CLI) operating as the cognitive reasoning and code-generation engine, the Manim Community Edition framework serving as the visual rendering engine, and local acoustic models like Coqui or Piper providing offline, latency-free vocal synthesis.2

By completely decoupling the generative process from proprietary, cloud-based text-to-speech APIs and manual video editing software, this architecture democratizes the production of STEM (Science, Technology, Engineering, and Mathematics) educational materials. The following sections provide a granular, algorithmic deconstruction of how to configure the Gemini CLI for headless execution, how to inject local file context using the @ inclusion operator, how to parse the resulting JSON payloads for executable Python code, and how to govern the Manim rendering context to achieve perfect audio-visual synchronization without human intervention.2

## 2. The Cognitive Engine: Google Gemini CLI Architecture

The foundation of the automated generative pipeline is the Google Gemini CLI. Unlike traditional web-based conversational interfaces, the Gemini CLI is an open-source, terminal-native AI agent designed explicitly for seamless integration into developer workflows, continuous integration/continuous deployment (CI/CD) pipelines, and autonomous shell scripts.4 It acts as the direct conduit to the Gemini 3 model family, providing access to a one-million token context window, which is critical when parsing extensive educational study guides or textbooks.4

## 2.1. Installation and Execution Environments

The Gemini CLI is distributed via the Node Package Manager (NPM) and requires a modern Node.js runtime environment. The global installation is achieved via the command npm install -g @google/gemini-cli, rendering the gemini executable globally accessible across the host operating system.4 For highly restricted environments, such as isolated Docker containers or automated build servers where global state modifications are undesirable, the CLI can be invoked ephemerally using npx @google/gemini-cli.4

Authentication is remarkably flexible, supporting direct OAuth flows via Google Accounts for individual developers, which provides a generous free tier of up to sixty requests per minute.4 For enterprise pipelines requiring higher rate limits and strict service-level agreements, authentication can be routed through Google Cloud Vertex AI by exporting the GOOGLE_API_KEY and setting the environment variable GOOGLE_GENAI_USE_VERTEXAI=true.4 This flexibility ensures the pipeline can scale from a local researcher's laptop to a distributed, cloud-native video generation factory.

## 2.2. Contextual Injection via the @ File Inclusion Operator

A critical requirement of the proposed pipeline is the ability to force the LLM to read a specific local document—in this case, @resources/ann_ec_study_guide.md—and restrict its code generation exclusively to the concepts of Chapter 2. The Gemini CLI facilitates this through the native @ file inclusion syntax.6

When the CLI parser encounters the @ symbol immediately followed by a file path within the prompt string, it executes a pre-processing step prior to transmitting the payload to the Gemini backend.6 The CLI reads the contents of the specified local file, applies Git-aware filtering if the file is part of a repository, and injects the raw textual content directly into the system prompt's context window.6 This architectural design bypasses the need for the developer to write complex Python or Bash wrapper scripts to concatenate file contents manually. By declaring @resources/ann_ec_study_guide.md, the pipeline explicitly grounds the Gemini model in the verified mathematical truths of the source material, significantly reducing the probability of algorithmic hallucinations or the introduction of extraneous, non-pedagogical concepts into the resulting Manim script.

## 2.3. Headless Mode and JSON Output Structuring

To function within a fully autonomous pipeline, the Gemini CLI must be entirely stripped of its interactive, conversational read-eval-print loop (REPL) interface. This isolation is achieved by invoking the CLI in "Headless Mode," triggered by the -p or --prompt flag.2 Headless mode instructs the CLI to execute a single, synchronous inference request and terminate immediately upon receiving the final token, printing the output directly to standard output (stdout).2

However, raw textual output is insufficient for an automated code-generation pipeline, as LLMs inherently wrap their generated source code in conversational pleasantries and Markdown formatting (e.g., fenced code blocks). To predictably parse the response, the pipeline must enforce structural rigidity using the --output-format json flag.2

By executing a command formatted as gemini -p "prompt text" --output-format json, the bash script orchestrating the pipeline captures a reliable, easily parsable data structure. The integration of command-line JSON processors, primarily jq, becomes the next vital step in extracting the raw Python code from the response payload.12

## 3. The Visual Rendering Engine: Manim Community Edition

Once the Gemini CLI generates the Python script, the code must be compiled into a video file. Manim (Mathematical Animation Engine) is the premier open-source programmatic animation framework. Originally developed by Grant Sanderson for the 3Blue1Brown YouTube channel, it has since been forked into a robust, developer-driven repository known as the Manim Community Edition.13

## 3.1. Object-Oriented Animation and The Scene Class

Manim operates on an entirely programmatic, object-oriented paradigm. Rather than manipulating keyframes on a timeline via a graphical user interface, the developer writes Python code that instantiates mathematical objects (Mobjects), defines their coordinate geometry on a continuous two-dimensional plane, and applies temporal transformations. The entirety of an animation sequence is contained within a Python class that inherits from the base Scene class.13

In the context of the user's specific prompt, the instruction explicitly demands the creation of class Chapter2Neuron(Scene). However, because the pipeline requires voiceover integration, this base class will be seamlessly overridden by the VoiceoverScene class provided by the manim-voiceover plugin.7 The construct(self) method within this class serves as the main execution thread, where all visual elements are instantiated and rendered to the screen.

## 3.2. Typographical Rigor: The Role of MathTex

A defining constraint within the generative prompt is the strict mandate: "Use MathTex for all equations, formulas, and single variable letters." This constraint is paramount for maintaining pedagogical authority.

Standard text rendering in Manim utilizes system fonts via the Text or MarkupText classes, rendering strings as vector paths based on TrueType or OpenType font files. Conversely, the MathTex class acts as a direct interface to a local LaTeX compiler (such as TeX Live or MiKTeX) installed on the host machine. When the Gemini CLI generates a line such as equation = MathTex(r"z = \mathbf{w}^\top \mathbf{x} + b"), the Manim engine extracts the raw string, wraps it in a temporary LaTeX document, compiles it into a Device Independent (DVI) or Portable Document Format (PDF) file, converts the mathematical glyphs into Scalable Vector Graphics (SVG), and finally translates those SVGs into manipulatable Bezier curves native to Manim's rendering space.

By enforcing this rule, the prompt ensures that all subscripts, superscripts, Greek letters (such as  and ), and linear algebra notation remain visually consistent with academic publication standards, preventing the LLM from attempting to render math using inadequate standard text classes.

## 3.3. Spatial Layout and Relative Positioning

One of the most complex challenges in programmatic animation generated by an LLM is spatial overlapping. Because the AI model lacks a visual feedback loop during inference, it cannot "see" if a newly drawn vector arrow obscures an existing text label.

The generative prompt elegantly mitigates this spatial conflict by enforcing the use of relative positioning methods: .next_to(), .shift(), and .to_edge(). Instead of predicting absolute Cartesian coordinates (e.g., [2, -1, 0]), the LLM is instructed to anchor new Mobjects relative to the bounding boxes of existing ones. For instance, when constructing the artificial neuron diagram in Part 1 of the prompt, the generated Python script will instantiate a central circle, and then position the inputs using arrow_x1.next_to(neuron_circle, LEFT, buff=1.0). This logical, anchor-based geometry drastically improves the visual coherence of zero-shot AI-generated animations.

## 4. Acoustic Synthesis and Synchronization: Local Text-to-Speech Integration

The true innovation of the requested pipeline lies in its ability to autonomously narrate the generated mathematical visualizations without human intervention. The synchronization of dynamically rendered graphical elements with synthetic speech has historically been a highly frictional process. The manim-voiceover plugin elegantly resolves this by allowing developers to define TTS logic natively within the Python scene structure.14

To ensure the pipeline operates with complete data sovereignty, zero ongoing API costs, and no network latency, the architecture eschews cloud-based TTS solutions (like OpenAI or Azure) in favor of deep-learning acoustic models running locally on the host machine.16

## 4.1. The VoiceoverScene Context Manager

The manim-voiceover plugin introduces a profound structural enhancement to the Manim framework through the use of Python context managers.7 The generative prompt requires the LLM to wrap its animation code inside with self.voiceover(text="...") as tracker: blocks.

This context manager fundamentally alters the temporal flow of the animation. When the Python interpreter evaluates the with statement, the plugin intercepts the text string and transmits it to the configured local TTS engine. The TTS engine synthesizes the speech, saves a compressed .mp3 or .wav audio file to a local cache directory, and critically, calculates the exact duration of the resulting audio waveform in floating-point seconds.19

This duration is yielded back to the Python script via the tracker.duration variable. The LLM utilizes this dynamic variable to scale the speed of its animations. When the script executes self.play(Write(equation), run_time=tracker.duration), the Manim rendering engine calculates the necessary frame interpolation so that the physical writing of the mathematical equation concludes precisely on the final syllable of the synthesized speech.7 Furthermore, the context manager imposes an execution lock; subsequent blocks of Python code are suspended until the audio playback finishes, ensuring that the visual narrative progresses in perfect lockstep with the spoken explanations.14

## 4.2. Local TTS Engine Configuration: Coqui TTS

Coqui TTS represents a highly capable, open-source neural text-to-speech framework optimized for generating human-like, expressive acoustic outputs. Coqui operates by utilizing sophisticated deep learning architectures, commonly employing a sequence-to-sequence model (like Tacotron 2) to convert input text into intermediate mel-spectrograms, followed by a vocoder neural network to convert the spectrograms into audible waveforms.16

Integrating Coqui into the manim-voiceover pipeline requires installing the specific Python extra via pip install "manim-voiceover[coqui]".16 Because Coqui relies heavily on tensor multiplication, it necessitates an active installation of PyTorch.16 The documentation explicitly advises ensuring compatibility by operating within a Python 3.9 environment to prevent dependency conflicts between NumPy and PyTorch.16

Within the AI-generated Python script, configuring Coqui is remarkably straightforward. At the beginning of the construct method, the LLM will output:

```python

self.set_speech_service(
    CoquiService(
        model_name="tts_models/en/ljspeech/tacotron2-DDC",
        progress_bar=False
    )
)

This single declaration routes all subsequent self.voiceover() commands through the local Coqui inference engine.19 The plugin inherently optimizes performance by calculating an MD5 hash of the prompt text. If a scene is re-rendered to tweak visual elements, the plugin checks the hash, discovers the cached .wav file, and bypasses the computationally expensive neural network inference, dramatically accelerating the iterative development cycle.19

```

## 4.3. Alternative Local TTS Engine: Piper TTS

While Coqui delivers exceptional acoustic quality, its reliance on PyTorch can render it computationally heavy, particularly on environments lacking dedicated graphical processing units (GPUs). An increasingly standard alternative within localized AI pipelines is Piper TTS.3

Piper is an ultra-fast, local neural text-to-speech engine optimized to run efficiently on standard central processing units (CPUs), even finding utility on low-power embedded devices like the Raspberry Pi.3 Piper circumvents heavy deep learning frameworks by exporting its acoustic models into the Open Neural Network Exchange (ONNX) format, allowing for rapid, low-latency inference. While manim-voiceover provides native wrappers for Coqui, Azure, and OpenAI, integrating Piper into the pipeline is achievable by instantiating a local Piper HTTP server or by invoking the Piper CLI asynchronously within a custom SpeechService subclass.18 For automated pipelines prioritizing execution speed over extreme vocal emotiveness, Piper serves as a highly resilient and lightweight acoustic solution.

## 4.4. System Audio Dependencies

To successfully compile the final video with embedded audio tracks, the host environment must possess several critical system-level dependencies. The manim-voiceover plugin leverages PyAudio for audio interfacing, which in turn requires the underlying C-library PortAudio.22 On Debian or Ubuntu-based distributions, these dependencies are satisfied by executing sudo apt install portaudio19-dev followed by pip install pyaudio.22 Additionally, to manipulate audio playback rates dynamically without altering pitch, the pipeline relies on Sound eXchange (SoX), installable via sudo apt-get install sox libsox-fmt-all.22 Finally, FFmpeg must be present in the system's PATH to perform the final multiplexing of the rendered MP4 frames and the concatenated WAV audio file into the finished pedagogical video.23

## 5. Deconstructing the Generative Prompt and Code Synthesis

The core of the automated pipeline is the zero-shot prompting strategy provided in the initial architectural specification. The prompt is highly prescriptive, deliberately constraining the generative space of the Gemini model to produce clean, sequential, and pedagogically sound Manim code. By mapping the prompt's instructions directly to the expected Python output, the mechanics of AI-assisted educational design become clear.

## 5.1. Part 1: Biological vs. Artificial Neuron Mapping

The prompt instructs the model to first display text comparing the biological components of a neuron (Dendrites, Synapses, Soma, Axon) to the artificial components (Inputs, Weights, Summation, Activation), followed by drawing a classic artificial neuron diagram.

The Gemini CLI parses this requirement and leverages Manim's grouping capabilities. It will predictably generate a VGroup or a Table to display the textual comparison, utilizing the Text class for readability. Following the text display, the model will orchestrate the drawing of the diagram using foundational geometric primitives. It will instantiate three Arrow objects, designated as , utilizing .next_to() methods to space them evenly along the Y-axis. The weights () will be rendered as MathTex and positioned slightly above the arrows. A central Circle is drawn to represent the neuron's summation and activation core, with all input arrows mathematically oriented to point toward the circle's bounding edge. The use of with self.voiceover(...) wraps each logical creation step, providing real-time narration of the architectural mapping.

## 5.2. Part 2: The Core Mathematics and Induced Local Field

The second phase requires the rendering of the precise mathematical formula for the induced local field:

The prompt includes a critical pedagogical constraint: "Highlight 'b' as the Bias and explain via text that it 'shifts the decision function'."

Gemini fulfills this by deeply utilizing the MathTex string parsing capabilities. The generated code will define the equation, and then invoke a color alteration specifically targeting the substring representing the bias:

```python

induced_field = MathTex(r"z = \sum_{i=1}^{m} w_i x_i + b = \mathbf{w}^\top \mathbf{x} + b")
induced_field.set_color_by_tex("b", YELLOW)
bias_explanation = Text("Bias shifts the decision function", font_size=24)
bias_explanation.next_to(induced_field, DOWN)

```

This specific isolation of variables visually anchors the learner's attention to the relevant mathematical concept precisely as the synthetic voiceover explains its geometric significance in hyperspace.

## 5.3. Part 3: Activation Functions

The prompt demands the sequential visualization of three distinct activation functions: Threshold, Sigmoid, and ReLU, formatted exactly using LaTeX piecewise notation.

The LLM will generate three separate MathTex objects, translating the requested text into valid LaTeX compilation strings (e.g., r"\text{ReLU}(z) = \max(0,z)"). Because the prompt specifies "Animate them appearing one by one," the Gemini model will structure three consecutive with self.voiceover() context managers. The first block will execute self.play(Write(threshold_eq)), pausing execution until the TTS engine finishes reading the definition. Subsequently, it will execute a .shift() or .next_to() operation to place the Sigmoid equation below the Threshold equation, executing the next visual generation without overlapping the prior formulas.

## 5.4. Part 4: The Perceptron Update Rule

Moving from inference to learning, the prompt targets the perceptron weight update mechanism:

The strict constraint to use MathTex ensures that the learning rate () and the vector notations () are rendered with proper typographical boldness and spacing. The prompt explicitly requires an annotation below the rule explaining the error component . The Gemini model achieves this by anchoring a Text object directly to the lower bound of the MathTex object, ensuring spatial harmony on the canvas while the generated voiceover dictates the principles of error-driven gradient descent approximations.

## 5.5. Part 5: The Worked Example and Variable Substitution

The final pedagogical requirement is the most cognitively demanding for the LLM, as it necessitates both code generation and mathematical arithmetic. The prompt provides the equation  and instructs the pipeline to substitute , subsequently solving for the output using the previously defined Threshold and Sigmoid functions.

The Gemini CLI executes this by generating a sequence of transformation animations. It typically leverages Manim's TransformMatchingTex or sequential ReplacementTransform functions to visually morph the equation from its algebraic state to its numerical state.

The generated Python logic reflects the arithmetic execution:

```python

step1 = MathTex(r"z = 2x_1 - x_2 + 0.5")
step2 = MathTex(r"z = 2(1) - 3 + 0.5")
step3 = MathTex(r"z = -0.5")

The model accurately calculates the outcome based on the prompt's provided logic. Because , it generates code demonstrating that the Threshold function yields . For the Sigmoid function, the LLM correctly evaluates the exponential denominator, generating the approximate result via MathTex(r"y = \sigma(-0.5) \approx 0.3775"). The seamless integration of this mathematical reasoning into executable visual code demonstrates the profound capability of the Gemini model as an educational design agent.

```

## 5.6. Scene Management and Temporal Pacing

To prevent visual clutter across a multi-minute video, the prompt dictates: "clearing the screen (FadeOut) between each part." This vital instruction simplifies the LLM's state management. At the conclusion of each of the five parts, the Gemini model generates a command similar to self.play(*[FadeOut(mobj) for mobj in self.mobjects]). This effectively wipes the canvas, allowing the LLM to treat each subsequent pedagogical step as an isolated visual environment, drastically reducing the probability of elements wandering off-screen or overlapping. Finally, the inclusion of periodic self.wait() commands allows the animation to "breathe," providing the viewer with crucial cognitive processing time between dense mathematical voiceovers.

## 6. Orchestrating the End-to-End Execution Pipeline

The final phase of architecting the automated system is the development of a master Bash script capable of gluing the Gemini CLI interface, the JSON parsing logic, and the Manim compilation engine into a single, synchronous operational thread.

## 6.1. Executing the Headless LLM Request

The orchestration script begins by invoking the Gemini CLI. The target file path (@resources/ann_ec_study_guide.md) and the exhaustive prompt defining the five-part animation are passed as a single string argument. Crucially, the --output-format json flag is appended to the command, ensuring the LLM's output bypasses standard terminal rendering and serializes into a predictable data structure.2 The output stream is redirected into a temporary file, gemini_response.json.

```bash

```

#!/bin/bash
# Step 1: Invoke Gemini CLI in headless mode with JSON output
gemini -p "Please read the content of @resources/ann_ec_study_guide.md... [Full Prompt]" \
       --output-format json > gemini_response.json

## 6.2. JSON Parsing and Code Extraction via jq

The raw JSON payload returned by the Gemini API contains a nested hierarchy of metadata, usage statistics, and the primary textual response. To isolate the text, the pipeline utilizes the command-line utility jq, a highly versatile JSON processor.12

```bash

# Step 2: Extract the text content from the JSON payload
RAW_MARKDOWN=$(jq -r '.response' gemini_response.json)

Because the Gemini model operates as an instruction-tuned assistant, the raw markdown string inevitably contains conversational artifacts (e.g., "Certainly, here is the Manim code for the neural network tutorial:"). Attempting to execute this string directly via the Python interpreter will trigger a fatal syntax error. The script must parse the string to extract exclusively the text contained between the standard Markdown Python fences (```python and ```).

```

This extraction is elegantly achieved using standard stream editors like awk or sed 12:

```bash

# Step 3: Filter string for executable Python code
echo "$RAW_MARKDOWN" | awk '/^```python/{flag=1; next} /^```/{flag=0} flag' > chapter_2_neuron.py

```

This algorithm iterates through the text line by line. When it encounters the opening Python fence, it toggles a boolean flag to true and begins piping the subsequent lines into the chapter_2_neuron.py file. The moment it encounters the closing fence, the flag toggles to false, terminating the write stream. The resulting Python file is now a sanitized, fully executable Manim script.12

## 6.3. Compiling the Animation with Local TTS

The final step of the orchestration script invokes the Manim compilation engine on the newly synthesized Python file.

```bash

```

# Step 4: Render the animation to MP4
manim -pqh chapter_2_neuron.py Chapter2Neuron

The flags appended to the manim command govern the execution parameters. The -p flag instructs the system to open the generated video file in the default media player immediately upon completion. The -qh flag forces the engine to render the video at "high quality" (1080p resolution at 60 frames per second), ensuring the mathematical typography remains crisply legible. The Chapter2Neuron argument specifies the exact Python class to evaluate, which is essential if the file contains multiple scene definitions.

During this compilation phase, the underlying VoiceoverScene logic seizes control of the audio processing. The local Coqui or Piper TTS engine spins up in the background.18 As the Python interpreter iterates through the script and encounters each self.voiceover(text="...") context block, the text is fed to the neural TTS model.7 The model synthesizes the waveform, dumps the audio file to the local cache, computes the duration, and hands control back to the Manim engine.19 Manim subsequently calculates the visual interpolation algorithms required to draw the neurons, equations, and graphs precisely within the allotted audio timeframe.7 Finally, Manim invokes FFmpeg to merge the visual .mp4 stream and the consolidated .wav audio track, finalizing the production pipeline.

## 7. Strategic Implications for Educational Content Scaling

The successful deployment of this automated pipeline represents a profound advancement in the scalability of educational technology. The integration of zero-shot programmatic code generation via the Gemini CLI with localized text-to-speech synthesis yields several strategic advantages.

## 7.1. Economic Efficiency and Decentralization

The traditional production lifecycle of educational video content is highly capital-intensive, requiring human intervention at the scripting, animating, recording, and editing stages. By relegating the entire process to a deterministic algorithmic pipeline 1, the marginal cost of producing a highly technical mathematical explainer video is reduced to the localized electrical cost of computing the Gemini inference, the TTS audio synthesis, and the Manim frame rendering. Furthermore, because the pipeline relies entirely on open-source tools (Gemini CLI free tiers, Coqui TTS, Piper, and Manim CE) running locally on consumer hardware, it bypasses the recurring subscription fees associated with cloud-based API inference endpoints.

## 7.2. Autonomous Multilingual Localization

The architecture of the manim-voiceover plugin provides an unparalleled mechanism for global localization. Because the visual animations (via run_time=tracker.duration) are strictly bound to the mathematical duration of the synthesized audio 7, translating an entire mathematical video from English to Mandarin requires zero manual re-editing.

A supplementary script can intercept the generated chapter_2_neuron.py file, extract the strings within the text="..." parameters, route them through a translation API, and replace them in the source code. Upon re-compiling the Manim scene with a Mandarin TTS model, the visual pacing automatically expands or contracts to match the cadence and duration of the newly synthesized language.22 This automated temporal alignment removes the most significant barrier to producing globally accessible STEM educational material.

## 8. Conclusion

The orchestration of the Google Gemini CLI, local neural text-to-speech engines like Coqui and Piper, and the programmatic Manim animation framework establishes a highly robust, autonomous pipeline for the generation of educational video content. By structuring prompts with explicit pedagogical constraints—such as the mandatory use of MathTex for typographical accuracy, spatial anchoring for visual clarity, and logic-driven screen clearing for temporal pacing—large language models can effectively operate as expert educational animators.

Executing this pipeline in headless mode, passing file context via the @ operator, and employing jq to parse structural JSON responses ensures the consistent generation of sanitized, executable Python code. Ultimately, the VoiceoverScene context manager serves as the critical bridge, perfectly synchronizing localized acoustic synthesis with programmatic mathematical visualizations. This architecture not only eliminates the frictional labor inherent in manual video production but fundamentally scales the capacity to disseminate rigorous, high-quality STEM education globally.

#### Works cited

SurajPatel04/manimVideoGenerate: An AI-powered pipeline that automatically generates Manim video animations from simple text descriptions. - GitHub, accessed March 19, 2026,

Automate tasks with headless mode - Gemini CLI, accessed March 19, 2026,

Create your AI digital voice clone locally with Piper TTS | Tutorial - YouTube, accessed March 19, 2026,

google-gemini/gemini-cli: An open-source AI agent that brings the power of Gemini directly into your terminal. - GitHub, accessed March 19, 2026,

Headless mode reference - Gemini CLI, accessed March 19, 2026,

CLI commands | Gemini CLI, accessed March 19, 2026,

openai-example.py - ManimCommunity/manim-voiceover - GitHub, accessed March 19, 2026,

Headless Mode | gemini-cli - GitHub Pages, accessed March 19, 2026,

Getting Started with Google's Gemini CLI | by Petipois | Mar, 2026, accessed March 19, 2026,

File management with Gemini CLI, accessed March 19, 2026,

Structured JSON Output #8022 - google-gemini/gemini-cli - GitHub, accessed March 19, 2026,

PSA - Extracting output from Gemini models - Tips & Tricks - n8n Community, accessed March 19, 2026,

Adding voiceovers to Manim videos directly in Python using Whisper #644 - GitHub, accessed March 19, 2026,

Adding Voiceovers to Videos - Manim Community v0.20.1, accessed March 19, 2026,

Manim Voiceover, accessed March 19, 2026,

Speech Services - Manim Voiceover v0.3.7, accessed March 19, 2026,

[N] Coqui TTS Local Installation Tutorial - Clone voices within seconds for free! - Reddit, accessed March 19, 2026,

Running a local Piper TTS server with Python on Linux - YouTube, accessed March 19, 2026,

manim_voiceover.services.coqui - Manim Voiceover v0.3.7, accessed March 19, 2026,

Manim Voiceover demo — basic example - YouTube, accessed March 19, 2026,

Piper - Pipecat, accessed March 19, 2026,

Installation - Manim Voiceover v0.3.7, accessed March 19, 2026,

Generate AI voiceovers from scripts with Gemini TTS and upload to Google Drive - N8N, accessed March 19, 2026,

Parse simple python JSON output through command line using jq - "cannot index string with string" - Stack Overflow, accessed March 19, 2026,

Writing hooks for Gemini CLI, accessed March 19, 2026,