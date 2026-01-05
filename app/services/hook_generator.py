"""
Hook Generator Service - POV-ALIGNED TRUST-BUILDING HOOKS
Generates scroll-stopping hooks that build BRAND TRUST, not just virality.

PHILOSOPHY:
- Contradiction hooks over curiosity spam
- POV-aligned framing
- Emotional immediacy over information teasing
- Trust-building over click-baiting
"""
import replicate
import asyncio
from typing import List, Dict, Optional
from loguru import logger

from app.core.config import settings
from app.services.youtube_analyzer import youtube_analyzer
from app.models.video import StoryLens


class HookGeneratorService:
    """
    Generate POV-ALIGNED hooks that build trust, not just virality.
    
    Key changes from spam hooks:
    - NO "99% don't know" (damages trust)
    - NO "School never taught" (overused)
    - NO "Video will be deleted" (manipulative)
    
    Instead use:
    - Contradictions (create genuine tension)
    - POV framing (consistent brand voice)
    - Emotional immediacy (feel, don't tease)
    """
    
    # ==========================================
    # DEPRECATED HOOKS - DO NOT USE
    # ==========================================
    DEPRECATED_HOOKS = [
        "99%", "99 %", "99percent",
        "school never taught", "school में नहीं",
        "video delete", "delete होने से पहले",
        "teachers never told", "teachers ने नहीं बताया",
        "secret revealed", "secret आज तक छुपा",
        "you won't believe", "believe नहीं करेंगे",
        "intelligent लोग ही", "only smart people",
    ]
    
    # ==========================================
    # POV-ALIGNED HOOK FORMULAS (Trust-Building)
    # ==========================================
    HOOK_FORMULAS = {
        # CONTRADICTION HOOKS - Create genuine tension
        "contradiction": [
            "जीत सामने थी... फिर एक फैसले ने सब बदल दिया",
            "जिसे सबसे ताकतवर माना गया... वही यहाँ डर रहा था",
            "इतिहास में पहली बार... जीत का मतलब हार था",
            "विश्वास था... पर विश्वासघात भी तय था",
            "सब कुछ सही था... सिवाय उस एक पल के",
        ],
        
        # POV HOOKS - Lens-specific emotional framing
        "power_pov": [
            "इस पल में... ताकत सबसे कमज़ोर थी",
            "जिसके पास सब था... उसने सब खो दिया",
            "राजा था... पर गुलाम बनने वाला था",
            "सत्ता के खेल में... सबसे बड़ी चाल",
        ],
        "fear_pov": [
            "उसका हाथ काँप रहा था... पर फैसला करना था",
            "डर था... पर रुकने का option नहीं था",
            "मौत सामने थी... फिर भी चलता रहा",
            "जब सब भागे... वो अकेला खड़ा रहा",
        ],
        "betrayal_pov": [
            "जिस पर भरोसा था... वही दुश्मन निकला",
            "एक हाथ मिलाया... दूसरे में छुपा था खंजर",
            "विश्वास तोड़ा गया... और इतिहास बदल गया",
            "दोस्त समझा था... गलती हो गई",
        ],
        "turning_point_pov": [
            "वो एक पल... जिसने सब बदल दिया",
            "एक फैसला... और इतिहास मुड़ गया",
            "अगर उस रात ये नहीं होता...",
            "सिर्फ 5 मिनट की देरी... और कुछ और होता",
        ],
        "underrated_pov": [
            "इस इंसान को भुला दिया गया... जानबूझकर",
            "ये कहानी क्यों नहीं सुनाई जाती?",
            "इतिहास ने इसे ignore किया... पर हम नहीं करेंगे",
            "जिसने बदला सब... पर नाम किसी को याद नहीं",
        ],
        
        # EMOTIONAL IMMEDIACY - Feel first, think later
        "emotional_immediacy": [
            "उस रात... कुछ होने वाला था",
            "सुबह होने से पहले... सब बदल जाना था",
            "ये वो पल था... जब सब ठहर गया",
            "आँखों में आँसू थे... पर हिम्मत नहीं हारी",
        ],
        
        # LEGACY - Some updated classic hooks (non-spam)
        "curiosity_genuine": [
            "ये कहानी सुनोगे तो सोच बदल जाएगी",
            "इतिहास का वो chapter जो छूट गया",
            "ये सच है... चाहे मानो या ना मानो",
            "कुछ कहानियाँ... सुनाई नहीं जातीं",
        ],
        "time_travel": [
            "चलो उस रात पर चलते हैं...",
            "अगर उस पल वहाँ होते...",
            "उस जगह... उस वक़्त... क्या हुआ था",
        ],
    }
    
    # Emotion triggers for Hindi audience (updated for trust-building)
    EMOTION_TRIGGERS = {
        "empathy": ["insaan", "dil", "himmat", "akela", "डर", "हिम्मत"],
        "tension": ["pل", "raat", "waqt", "subah", "पल", "रात"],
        "pride": ["bharatiya", "hamara", "proud", "india", "desh"],
        "curiosity": ["kahani", "raaz", "sach", "कहानी", "सच"],
        "anger": ["vishwasghaat", "dhoka", "विश्वासघात", "धोखा"],
        "inspiration": ["himmat", "akela", "khada", "हिम्मत", "अकेला"],
    }
    
    # Story lens to hook formula mapping
    LENS_TO_FORMULAS = {
        StoryLens.POWER: ["power_pov", "contradiction"],
        StoryLens.FEAR: ["fear_pov", "emotional_immediacy"],
        StoryLens.BETRAYAL: ["betrayal_pov", "contradiction"],
        StoryLens.TURNING_POINT: ["turning_point_pov", "emotional_immediacy"],
        StoryLens.UNDERRATED: ["underrated_pov", "curiosity_genuine"],
    }
    
    def __init__(self):
        self.llm_model = settings.SCRIPT_MODEL
        self.reasoning_effort = "low"  # Fast hooks, less reasoning needed
        self.verbosity = settings.LLM_VERBOSITY
    
    async def generate_viral_hook(
        self, 
        topic: str, 
        era: str, 
        mood: str = "dramatic",
        story_lens: StoryLens = StoryLens.TURNING_POINT,
        use_youtube_analysis: bool = True
    ) -> Dict:
        """
        Generate POV-ALIGNED, trust-building hook for a topic.
        Uses story lens to ensure consistent brand voice.
        """
        logger.info(f"🎯 Generating POV-aligned hook for: {topic}")
        logger.info(f"   Story Lens: {story_lens.value}")
        
        # Step 1: Get YouTube viral analysis (for engagement patterns, not hooks)
        viral_insights = {}
        if use_youtube_analysis:
            try:
                viral_insights = await youtube_analyzer.analyze_viral_patterns()
            except Exception as e:
                logger.warning(f"YouTube analysis failed: {e}")
        
        # Step 2: Search for similar viral content
        similar_content = []
        try:
            similar_content = await youtube_analyzer.search_similar_viral_content(topic, 5)
        except Exception as e:
            logger.warning(f"Similar content search failed: {e}")
        
        # Step 3: Generate hooks using LLM with POV lens
        hooks = await self._generate_hooks_with_llm(
            topic=topic,
            era=era,
            mood=mood,
            story_lens=story_lens,
            viral_insights=viral_insights,
            similar_content=similar_content
        )
        
        # Step 4: Filter out deprecated spam hooks
        filtered_hooks = self._filter_deprecated_hooks(hooks)
        
        # Step 5: Score and rank hooks (with POV alignment bonus)
        ranked_hooks = self._rank_hooks(filtered_hooks, mood, story_lens)
        
        return {
            "best_hook": ranked_hooks[0] if ranked_hooks else self._get_fallback_hook(topic, era, story_lens),
            "alternative_hooks": ranked_hooks[1:5] if len(ranked_hooks) > 1 else [],
            "hook_type": mood,
            "story_lens": story_lens.value,
            "viral_insights_used": bool(viral_insights),
            "similar_viral_titles": [c['title'] for c in similar_content[:3]]
        }
    
    def _filter_deprecated_hooks(self, hooks: List[str]) -> List[str]:
        """Filter out hooks that contain deprecated spam patterns."""
        filtered = []
        for hook in hooks:
            hook_lower = hook.lower()
            is_spam = any(spam in hook_lower for spam in self.DEPRECATED_HOOKS)
            if not is_spam:
                filtered.append(hook)
            else:
                logger.debug(f"Filtered spam hook: {hook[:30]}...")
        
        # If all hooks were spam, return originals to avoid empty list
        return filtered if filtered else hooks[:3]
    
    async def _generate_hooks_with_llm(
        self,
        topic: str,
        era: str,
        mood: str,
        story_lens: StoryLens,
        viral_insights: Dict,
        similar_content: List[Dict]
    ) -> List[str]:
        """Generate POV-ALIGNED hooks using LLM with story lens context."""
        
        # Format viral insights (for engagement patterns only)
        viral_context = ""
        if viral_insights.get('top_hooks'):
            viral_context = "Reference for engagement (NOT for copying hooks):\n" + \
                "\n".join([f"- {h['title']}" for h in viral_insights['top_hooks'][:3]])
        
        # Format similar content
        similar_context = ""
        if similar_content:
            similar_context = "Similar content (for context):\n" + \
                "\n".join([f"- {c['title']}" for c in similar_content[:3]])
        
        # Get POV-aligned formula hooks as examples
        formula_examples = self._get_formula_hooks(topic, era, mood, story_lens)
        
        # Story lens specific instructions
        lens_instructions = {
            StoryLens.POWER: "Focus on POWER DYNAMICS - who had power, who lost it, the moment of shift",
            StoryLens.FEAR: "Focus on FEAR becoming COURAGE - the human hesitation before the brave act",
            StoryLens.BETRAYAL: "Focus on TRUST BROKEN - the knife in the back, loyalty tested",
            StoryLens.TURNING_POINT: "Focus on THE ONE DECISION - the irreversible choice that changed everything",
            StoryLens.UNDERRATED: "Focus on FORGOTTEN/IGNORED - why this was hidden, who benefited from forgetting",
        }
        
        prompt = f"""You are a MASTER STORYTELLER for Hindi Instagram Reels.
You create hooks that build TRUST, not just clicks.

TOPIC: {topic}
ERA: {era}
MOOD: {mood}
STORY LENS: {story_lens.value}
LENS FOCUS: {lens_instructions[story_lens]}

{viral_context}

{similar_context}

GOOD HOOK EXAMPLES (POV-aligned):
{chr(10).join(f'- {h}' for h in formula_examples[:6])}

=== ⚠️ CRITICAL: DO NOT USE THESE SPAM PATTERNS ===
❌ "99% लोग नहीं जानते" - SPAM, damages trust
❌ "School में नहीं पढ़ाया" - OVERUSED
❌ "Video delete होने से पहले" - MANIPULATIVE
❌ "सिर्फ intelligent लोग" - INSULTING
❌ "आपको believe नहीं होगा" - CLICKBAIT

=== ✅ USE THESE TRUST-BUILDING PATTERNS ===
✅ CONTRADICTION: "जीत सामने थी... फिर सब बदल गया"
✅ TENSION: "उस रात... कुछ होने वाला था"
✅ EMOTION: "उसका हाथ काँप रहा था..."
✅ POV FRAMING: "इस पल में ताकत सबसे कमज़ोर थी"

YOUR TASK:
Generate 10 UNIQUE hooks that:
1. Create TENSION or CONTRADICTION (not curiosity bait)
2. Align with the {story_lens.value} POV lens
3. Make viewer FEEL something immediately
4. Build TRUST (you will answer the question raised)
5. HINDI DEVANAGARI SCRIPT only
6. Under 15 words

OUTPUT FORMAT:
Just list 10 hooks, one per line. No numbering, no explanation.

Generate 10 POV-aligned, trust-building hooks:"""

        try:
            output = replicate.run(
                self.llm_model,
                input={
                    "prompt": prompt,
                    "messages": [],
                    "verbosity": self.verbosity,
                    "reasoning_effort": self.reasoning_effort,
                }
            )
            
            # GPT-5.2 returns string directly, not iterator
            response = output if isinstance(output, str) else "".join(output)
            
            # Parse hooks from response
            hooks = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 10:
                    # Remove numbering if present
                    line = line.lstrip('0123456789.-) ')
                    hooks.append(line)
            
            return hooks[:10]
            
        except Exception as e:
            logger.error(f"LLM hook generation failed: {e}")
            return formula_examples
    
    def _get_formula_hooks(
        self, 
        topic: str, 
        era: str, 
        mood: str,
        story_lens: StoryLens = StoryLens.TURNING_POINT
    ) -> List[str]:
        """Get POV-aligned hooks from formulas based on story lens."""
        hooks = []
        
        # Primary: Get formulas aligned to story lens
        lens_formulas = self.LENS_TO_FORMULAS.get(
            story_lens, 
            ["contradiction", "emotional_immediacy"]
        )
        
        for category in lens_formulas:
            formulas = self.HOOK_FORMULAS.get(category, [])
            for formula in formulas[:3]:
                # Some formulas have placeholders
                try:
                    hook = formula.format(topic=topic, era=era)
                except KeyError:
                    hook = formula
                hooks.append(hook)
        
        # Secondary: Add some general trust-building hooks
        general_categories = ["contradiction", "emotional_immediacy", "curiosity_genuine"]
        for category in general_categories:
            if category not in lens_formulas:
                formulas = self.HOOK_FORMULAS.get(category, [])
                for formula in formulas[:2]:
                    try:
                        hook = formula.format(topic=topic, era=era)
                    except KeyError:
                        hook = formula
                    if hook not in hooks:
                        hooks.append(hook)
        
        return hooks[:10]
    
    def _rank_hooks(
        self, 
        hooks: List[str], 
        mood: str,
        story_lens: StoryLens = StoryLens.TURNING_POINT
    ) -> List[str]:
        """
        Score and rank hooks based on TRUST-BUILDING potential.
        Prioritizes POV alignment and emotional immediacy over virality tricks.
        """
        
        scored_hooks = []
        
        for hook in hooks:
            score = 0
            hook_lower = hook.lower()
            
            # ==========================================
            # NEGATIVE SCORES - Penalize spam patterns
            # ==========================================
            for spam in self.DEPRECATED_HOOKS:
                if spam in hook_lower:
                    score -= 20  # Heavy penalty for spam
            
            # Penalize overused patterns
            if '99%' in hook or '99 %' in hook:
                score -= 30
            if 'believe नहीं' in hook_lower or 'believe nahi' in hook_lower:
                score -= 15
            
            # ==========================================
            # POSITIVE SCORES - Reward trust-building
            # ==========================================
            
            # Length score (shorter is better for hooks)
            if len(hook) < 50:
                score += 10
            elif len(hook) < 80:
                score += 5
            
            # Emotion triggers (updated for trust-building)
            for emotion, triggers in self.EMOTION_TRIGGERS.items():
                for trigger in triggers:
                    if trigger in hook_lower or trigger in hook:
                        score += 6
            
            # Ellipsis usage (creates natural tension) "..."
            if '...' in hook:
                score += 8
            
            # Contradiction indicators (good for trust-building)
            contradiction_words = ['पर', 'फिर', 'मगर', 'लेकिन', 'par', 'phir', 'lekin']
            for word in contradiction_words:
                if word in hook_lower:
                    score += 10  # High score for contradictions
                    break
            
            # Human emotion words (creates empathy)
            emotion_words = ['डर', 'हिम्मत', 'काँप', 'आँसू', 'अकेला', 'dar', 'himmat', 'aansoo']
            for word in emotion_words:
                if word in hook_lower or word in hook:
                    score += 8
            
            # POV-specific bonus words
            lens_bonus_words = {
                StoryLens.POWER: ['ताकत', 'सत्ता', 'राजा', 'power', 'taakat'],
                StoryLens.FEAR: ['डर', 'हिम्मत', 'भागे', 'dar', 'himmat'],
                StoryLens.BETRAYAL: ['विश्वासघात', 'धोखा', 'दुश्मन', 'dhoka'],
                StoryLens.TURNING_POINT: ['फैसला', 'पल', 'बदल', 'faisla', 'pal'],
                StoryLens.UNDERRATED: ['भुला', 'ignore', 'छुपा', 'नाम', 'naam'],
            }
            for word in lens_bonus_words.get(story_lens, []):
                if word in hook_lower or word in hook:
                    score += 7
            
            # Hindi conversational starters (natural feel)
            starters = ['उस', 'वो', 'जब', 'जिस', 'ये', 'देखो', 'सुनो']
            for starter in starters:
                if hook.startswith(starter):
                    score += 5
                    break
            
            # Penalize question marks (often clickbaity)
            if '?' in hook:
                score -= 3  # Slight penalty - contradictions work better
            
            scored_hooks.append((hook, score))
        
        # Sort by score descending
        scored_hooks.sort(key=lambda x: x[1], reverse=True)
        
        return [h[0] for h in scored_hooks]
    
    def _get_fallback_hook(
        self, 
        topic: str, 
        era: str,
        story_lens: StoryLens = StoryLens.TURNING_POINT
    ) -> str:
        """POV-aligned fallback hook if generation fails."""
        # Different fallbacks based on lens
        lens_fallbacks = {
            StoryLens.POWER: f"इस पल में... ताकत सबसे कमज़ोर थी",
            StoryLens.FEAR: f"उसका हाथ काँप रहा था... पर रुकना नहीं था",
            StoryLens.BETRAYAL: f"जिस पर भरोसा था... वही सबसे बड़ा दुश्मन निकला",
            StoryLens.TURNING_POINT: f"वो एक फैसला... जिसने सब बदल दिया",
            StoryLens.UNDERRATED: f"ये कहानी... जानबूझकर भुला दी गई",
        }
        return lens_fallbacks.get(story_lens, f"ये कहानी... आपकी सोच बदल देगी")
    
    async def generate_multiple_hooks(
        self, 
        topic: str, 
        era: str, 
        count: int = 10
    ) -> List[str]:
        """Generate multiple hooks for A/B testing"""
        result = await self.generate_viral_hook(topic, era)
        
        all_hooks = [result['best_hook']] + result.get('alternative_hooks', [])
        
        # Add formula hooks to fill
        formula_hooks = self._get_formula_hooks(topic, era, "dramatic")
        all_hooks.extend(formula_hooks)
        
        # Remove duplicates and return
        unique_hooks = list(dict.fromkeys(all_hooks))
        return unique_hooks[:count]


# Singleton instance
hook_generator = HookGeneratorService()

