import asyncio
import azure.cognitiveservices.speech as speechsdk
from loguru import logger

from constants import config


async def synthesize_speech(text: str, output_file: str, voice: str = "en-SG-WayneNeural"):  # Singapore English, Wayne
    if not config.azure.tts_speech_key:
        logger.warning("[Azure TTS] 没有检测到 tts_speech_key，不进行语音转换。")
        return False
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    def create_synthesizer():
        speech_key, service_region = config.azure.tts_speech_key, config.azure.tts_speech_service_region
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        # https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts#neural-voices
        speech_config.set_property(speechsdk.PropertyId.SpeechServiceConnection_SynthVoice, voice)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        return speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # result = await asyncio.get_event_loop().run_in_executor(None, synthesizer.speak_text_async(text).get)
    # result = synthesizer.speak_text_async(text).get()
    synthesizer = await loop.run_in_executor(None, create_synthesizer)
    loop.call_soon_threadsafe(run_synthesize_speech, synthesizer, text, future)

    return await future

def run_synthesize_speech(synthesizer, text, future):
    result = synthesizer.speak_text_async(text).get()
    future.set_result(result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted)
