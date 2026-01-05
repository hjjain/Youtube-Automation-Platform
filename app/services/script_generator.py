"""
Script Generation Service - POV-FIRST STORYTELLING
Generates Hindi narration scripts with INTERPRETATION, not just information.

STORY STRUCTURE:
Hook (Contradiction) → Human Tension → Decision Moment → Consequence → Meaning

This builds TRUST through complete stories, not curiosity bait.
"""
import replicate
from typing import Optional, List
from loguru import logger

from app.core.config import settings
from app.models.video import (
    VideoScript, ScriptSegment, MusicMood, VideoRequest,
    StoryLens, EmotionalState
)
from app.services.hook_generator import hook_generator
from app.services.youtube_analyzer import youtube_analyzer


class ScriptGeneratorService:
    """
    POV-First Script Generator
    
    Key principles:
    1. INTERPRETATION over information - we tell MEANING, not facts
    2. Emotional arc with clear states (tension → fear → decision → impact → reflection)
    3. Complete stories that ANSWER questions, not just raise them
    4. Consistent POV through story lens
    """
    
    # Emotional arc structure for each segment position
    EMOTIONAL_ARC = {
        1: EmotionalState.TENSION,      # Hook - create unease
        2: EmotionalState.TENSION,      # Build context with tension
        3: EmotionalState.FEAR,         # The danger/stakes become real
        4: EmotionalState.FEAR,         # Stakes intensify
        5: EmotionalState.DECISION,     # The pivotal moment
        6: EmotionalState.IMPACT,       # The consequence
        7: EmotionalState.IMPACT,       # The aftermath
        8: EmotionalState.REFLECTION,   # The meaning
    }
    
    def __init__(self):
        self.model = settings.SCRIPT_MODEL
        self.reasoning_effort = settings.LLM_REASONING_EFFORT
        self.verbosity = settings.LLM_VERBOSITY
    
    async def generate_script(self, request: VideoRequest) -> VideoScript:
        """
        Generate a POV-FIRST script with complete emotional arc.
        Focus: INTERPRETATION over information.
        """
        logger.info(f"🎬 Generating POV-first script for: {request.topic}")
        logger.info(f"🎯 Story Lens: {request.story_lens.value}")
        
        # Step 1: Generate POV-aligned hook
        logger.info("Step 1: Generating POV-aligned hook...")
        hook_result = await hook_generator.generate_viral_hook(
            topic=request.topic,
            era=request.era,
            mood=request.music_mood.value,
            story_lens=request.story_lens
        )
        
        best_hook = hook_result['best_hook']
        logger.info(f"Best hook: {best_hook}")
        
        # Step 2: Get similar viral content for reference
        similar_content = hook_result.get('similar_viral_titles', [])
        
        # Step 3: Generate full script with emotional arc
        prompt = self._build_pov_prompt(request, best_hook, similar_content)
        
        try:
            output = replicate.run(
                self.model,
                input={
                    "prompt": prompt,
                    "messages": [],
                    "verbosity": self.verbosity,
                    "reasoning_effort": self.reasoning_effort,
                }
            )
            
            # GPT-5.2 returns string directly, not iterator
            response_text = output if isinstance(output, str) else "".join(output)
            logger.debug(f"Raw GPT-5.2 response: {response_text[:500]}...")
            
            # Parse response into script with emotional states
            script = self._parse_response(response_text, request, best_hook)
            logger.info(f"Generated script with {len(script.segments)} segments")
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            raise
    
    def _build_pov_prompt(
        self, 
        request: VideoRequest, 
        hook: str,
        similar_content: list
    ) -> str:
        """
        Build prompt for POV-FIRST storytelling.
        Focus: INTERPRETATION over information.
        Structure: Hook → Human Tension → Decision Moment → Consequence → Meaning
        """
        
        # Story lens specific instructions
        lens_instructions = {
            StoryLens.POWER: """
LENS: POWER & CONTROL
Tell this story through the lens of power dynamics.
- Who had power? Who lost it?
- What was the moment of power shift?
- Focus on dominance, control, authority being gained or lost""",
            
            StoryLens.FEAR: """
LENS: FEAR TO COURAGE
Tell this story through the lens of fear becoming courage.
- What was the human FEAR before the brave act?
- Show the hesitation, the doubt, the pressure
- The moment of choosing courage over safety""",
            
            StoryLens.BETRAYAL: """
LENS: BETRAYAL & CONSEQUENCES
Tell this story through the lens of trust being broken.
- Who betrayed whom? Why?
- What was the cost of betrayal?
- Focus on loyalty tested and found wanting""",
            
            StoryLens.TURNING_POINT: """
LENS: SINGLE DECISION MOMENTS
Tell this story through ONE irreversible choice.
- What was the EXACT moment when everything changed?
- Before vs After that decision
- The weight of that one choice""",
            
            StoryLens.UNDERRATED: """
LENS: HISTORY IGNORED THIS
Tell this story as the one history forgot.
- Why was this hidden/ignored?
- Who benefited from this being forgotten?
- The injustice of this not being known""",
        }
        
        lens_context = lens_instructions.get(request.story_lens, lens_instructions[StoryLens.TURNING_POINT])
        
        similar_context = ""
        if similar_content:
            similar_context = f"""
REFERENCE - Similar viral videos (for engagement style):
{chr(10).join(f'- {title}' for title in similar_content[:3])}
"""
        
        prompt = f"""You are a MASTER STORYTELLER for Hindi Instagram Reels.
You tell INTERPRETED HISTORY - not facts, but MEANING.
You make viewers FEEL the moment, not just know about it.

TOPIC: {request.topic}
ERA: {request.era}
TARGET DURATION: 35-40 seconds of narration
NUMBER OF SEGMENTS: {request.num_segments}
MOOD: {request.music_mood.value}
{lens_context}

HOOK TO USE (Opening line):
"{hook}"

{similar_context}

=== ⚠️ THE CREATOR MINDSET (CRITICAL!) ===

YOU ARE NOT AN EXPLAINER. YOU ARE AN INTERPRETER.

❌ EXPLAINER (Don't do this):
"1857 में मंगल पांडे ने विद्रोह शुरू किया। उन्होंने British officers पर गोली चलाई। 
फिर उन्हें फांसी दी गई। यह था भारत की पहली freedom struggle।"
(This is Wikipedia. Boring. No emotion.)

✅ INTERPRETER (Do this):
"उस रात मंगल पांडे का हाथ काँप रहा था... बंदूक भारी लग रही थी।
गोली चलाने का मतलब था... मौत पक्की।
फिर भी उसने trigger दबाया... क्योंकि गुलामी... मौत से भी बुरी थी।
वो एक गोली... 90 साल की आज़ादी की लड़ाई की शुरुआत थी।"
(This is FELT. Human. Emotional.)

=== NEW STORY STRUCTURE (MANDATORY) ===

Follow this EXACT emotional arc:

1. HOOK (TENSION): Contradiction or tension that grabs attention
   - NOT "99% don't know" spam
   - Create unease, make them feel something is off
   
2. HUMAN TENSION (FEAR): The fear, doubt, pressure the person felt
   - What was at stake?
   - What could go wrong?
   - The human hesitation before action

3-4. DECISION MOMENT (DECISION): THE ONE irreversible choice
   - The exact moment of no return
   - What made them decide?
   - Show the weight of the decision

5-6. CONSEQUENCE (IMPACT): Good or bad, what happened
   - The immediate result
   - The ripple effects
   - What changed forever

7-8. MEANING (REFLECTION): Why this still matters
   - The lesson or insight
   - Why we should care today
   - Leave them thinking

=== EMOTIONAL STATE FOR EACH SEGMENT ===

Mark each segment with its emotional state:
SEGMENT 1: EMOTION: tension
SEGMENT 2: EMOTION: tension  
SEGMENT 3: EMOTION: fear
SEGMENT 4: EMOTION: fear
SEGMENT 5: EMOTION: decision
SEGMENT 6: EMOTION: impact
SEGMENT 7: EMOTION: impact
SEGMENT 8: EMOTION: reflection

=== WRITING RULES ===

1. LANGUAGE: Write in HINDI DEVANAGARI SCRIPT (हिंदी में लिखें)
   - English proper nouns OK: "Delhi Sultanate", "Kakatiya"
   - NUMBERS IN ENGLISH: "1857" NOT "१८५७"
   
2. NARRATION STYLE:
   - Avoid dates/names overload
   - Focus on FEAR, HESITATION, POWER, BETRAYAL
   - Use pauses (...) for drama
   - Make viewer FEEL the moment
   
3. TOTAL NARRATION: 80-100 Hindi words (~40 seconds)
   - Each segment: 10-15 words
   
4. COMPLETE THE STORY: Answer every question raised!

=== OUTPUT FORMAT ===

SEGMENT 1:
NARRATION: [Hook - tension building]
IMAGE_PROMPT: [Detailed cinematic description - human-focused, close perspective]
EMOTION: tension
DURATION: 5

SEGMENT 2:
NARRATION: [Build tension - context]
IMAGE_PROMPT: [Scene setting - documentary style, close human perspective]
EMOTION: tension
DURATION: 5

... continue for all {request.num_segments} segments ...

=== IMAGE PROMPT GUIDELINES ===

VISUAL IDENTITY RULES (for brand consistency):
- Color palette: Warm amber + deep shadows
- Lighting: Low-key cinematic (not bright, not fantasy)
- Camera: Close HUMAN perspective (not god-view, not epic wide shots)
- Style: Documentary cinematic, NOT fantasy/mythic

For {request.era}:
- Close-up on HUMAN EMOTIONS (faces, hands, eyes)
- Intimate observational moments
- NOT epic battle panoramas
- NOT fantasy landscapes

⚠️ SAFETY: No weapons, violence, blood. Show the FEELING, not the action.
Example: Instead of "battle scene" → "soldier's face in torchlight, fear in eyes, fort silhouette behind"

=== EXAMPLE OF GOOD INTERPRETATION ===

Topic: Battle of Plassey

SEGMENT 1:
NARRATION: जीत... तय थी। पर किसी को पता नहीं था... किसकी।
IMAGE_PROMPT: Close-up of Mir Jafar's face in dim candlelight, conflicted expression, shadows on wall, warm amber tones, documentary cinematic, 8K
EMOTION: tension
DURATION: 5

SEGMENT 5 (DECISION):
NARRATION: उस रात Mir Jafar ने अपनी तलवार नीचे रख दी... और एक empire बेच दिया।
IMAGE_PROMPT: Man's hands placing something down in candlelight, shadows heavy, low-key cinematic lighting, close intimate shot
EMOTION: decision
DURATION: 5

Now generate the complete script with INTERPRETATION, not information:"""
        
        return prompt
    
    def _parse_response(
        self, 
        response: str, 
        request: VideoRequest,
        hook: str
    ) -> VideoScript:
        """Parse LLM response into structured VideoScript with emotional states"""
        
        segments = []
        current_segment = {}
        segment_num = 0
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Clean markdown formatting
            clean_line = line.replace('**', '').replace('*', '').strip()
            
            # Check for segment marker (handles various formats)
            if 'SEGMENT' in clean_line.upper() and any(c.isdigit() for c in clean_line):
                if current_segment and 'narration' in current_segment:
                    segments.append(self._create_segment(current_segment, segment_num))
                segment_num += 1
                current_segment = {}
                
            elif clean_line.upper().startswith('NARRATION:'):
                narration = clean_line.split(':', 1)[1].strip().strip('"') if ':' in clean_line else ''
                current_segment['narration'] = narration
                
            elif clean_line.upper().startswith('IMAGE_PROMPT:'):
                prompt = clean_line.split(':', 1)[1].strip().strip('"') if ':' in clean_line else ''
                current_segment['image_prompt'] = prompt
                
            elif clean_line.upper().startswith('EMOTION:'):
                emotion = clean_line.split(':', 1)[1].strip().lower() if ':' in clean_line else 'tension'
                current_segment['emotion'] = emotion
                
            elif clean_line.upper().startswith('DURATION:'):
                try:
                    duration_str = clean_line.split(':', 1)[1].strip() if ':' in clean_line else '5'
                    duration_str = duration_str.replace('seconds', '').replace('sec', '').strip()
                    current_segment['duration'] = float(duration_str) if duration_str else 5.0
                except ValueError:
                    current_segment['duration'] = request.target_duration / request.num_segments
        
        # Add last segment
        if current_segment and 'narration' in current_segment:
            segments.append(self._create_segment(current_segment, segment_num))
        
        # Ensure first segment has our hook
        if segments and segments[0].narration_text != hook:
            segments[0] = ScriptSegment(
                segment_number=1,
                narration_text=hook,
                image_prompt=segments[0].image_prompt,
                duration_seconds=segments[0].duration_seconds,
                emotional_state=segments[0].emotional_state
            )
        
        # If parsing failed, create default segments
        if not segments:
            logger.warning("Failed to parse LLM response, creating default segments")
            segments = self._create_default_segments(request, hook)
        
        # Assign emotional states based on arc if not provided
        for i, segment in enumerate(segments):
            if segment.emotional_state == EmotionalState.TENSION:
                # Use arc-based emotion if segment didn't specify
                arc_emotion = self.EMOTIONAL_ARC.get(i + 1, EmotionalState.TENSION)
                segments[i] = ScriptSegment(
                    segment_number=segment.segment_number,
                    narration_text=segment.narration_text,
                    image_prompt=segment.image_prompt,
                    duration_seconds=segment.duration_seconds,
                    emotional_state=arc_emotion
                )
        
        # Calculate total duration
        total_duration = sum(s.duration_seconds for s in segments)
        
        # Determine music mood
        music_mood = request.music_mood
        
        return VideoScript(
            title=request.topic,
            hook=hook,
            segments=segments,
            total_duration=total_duration,
            music_mood=music_mood,
            historical_era=request.era,
            event_description=request.topic,
            story_lens=request.story_lens
        )
    
    def _create_segment(self, data: dict, segment_num: int) -> ScriptSegment:
        """Create a ScriptSegment from parsed data with emotional state"""
        # Parse emotional state from string
        emotion_str = data.get('emotion', 'tension').lower()
        emotion_map = {
            'tension': EmotionalState.TENSION,
            'fear': EmotionalState.FEAR,
            'decision': EmotionalState.DECISION,
            'impact': EmotionalState.IMPACT,
            'reflection': EmotionalState.REFLECTION,
        }
        emotional_state = emotion_map.get(emotion_str, EmotionalState.TENSION)
        
        return ScriptSegment(
            segment_number=segment_num,
            narration_text=data.get('narration', ''),
            image_prompt=data.get('image_prompt', ''),
            duration_seconds=data.get('duration', 4.0),
            emotional_state=emotional_state
        )
    
    def _create_default_segments(self, request: VideoRequest, hook: str) -> List[ScriptSegment]:
        """Create default segments with emotional arc if parsing fails"""
        duration_per_segment = request.target_duration / request.num_segments
        segments = []
        
        # First segment always has the hook with tension
        segments.append(ScriptSegment(
            segment_number=1,
            narration_text=hook,
            image_prompt=f"Dramatic close-up opening scene from {request.era}, {request.topic}, warm amber lighting, documentary cinematic, 8K",
            duration_seconds=duration_per_segment,
            emotional_state=EmotionalState.TENSION
        ))
        
        for i in range(1, request.num_segments):
            # Get emotional state from arc
            arc_emotion = self.EMOTIONAL_ARC.get(i + 1, EmotionalState.TENSION)
            
            segments.append(ScriptSegment(
                segment_number=i + 1,
                narration_text=f"[Segment {i + 1} narration]",
                image_prompt=f"Historical scene from {request.era}, {request.topic}, close human perspective, low-key cinematic, 8K",
                duration_seconds=duration_per_segment,
                emotional_state=arc_emotion
            ))
        
        return segments


# Singleton instance
script_generator = ScriptGeneratorService()
