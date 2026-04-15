"""
Voice output for MantisClaw using edge-tts.
Generates speech and plays it via system audio.
"""

import asyncio
import logging
import os
import subprocess
import sys
import tempfile

import edge_tts

logger = logging.getLogger("mantisclaw.voice")


class VoiceOutput:
    """Text-to-Speech output using Microsoft Edge TTS."""

    def __init__(self, voice: str = "de-DE-KatjaNeural", enabled: bool = True):
        self.voice = voice
        self.enabled = enabled

    async def speak(self, text: str) -> bool:
        """Generate TTS and play audio. Returns True on success."""
        if not self.enabled or not text.strip():
            return False

        tmpfile = None
        try:
            fd, tmpfile = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(tmpfile)

            logger.debug(f"Voice: {text[:80]}...")
            self._play(tmpfile)
            return True
        except Exception as e:
            logger.error(f"Voice output failed: {e}")
            return False
        finally:
            if tmpfile and os.path.exists(tmpfile):
                try:
                    os.unlink(tmpfile)
                except OSError:
                    pass

    def _play(self, filepath: str):
        """Play mp3 file using platform-appropriate method."""
        if sys.platform == "win32":
            self._play_windows(filepath)
        else:
            self._play_unix(filepath)

    def _play_windows(self, filepath: str):
        """Play mp3 using PowerShell + .NET WPF MediaPlayer."""
        # Use forward slashes for URI compatibility
        uri_path = filepath.replace("\\", "/")
        ps_script = (
            'Add-Type -AssemblyName presentationCore; '
            '$p = New-Object System.Windows.Media.MediaPlayer; '
            f'$p.Open([uri]::new("file:///{uri_path}")); '
            'Start-Sleep -Milliseconds 500; '
            '$p.Play(); '
            'while(-not $p.NaturalDuration.HasTimeSpan){'
            'Start-Sleep -Milliseconds 100}; '
            '$d = [int]$p.NaturalDuration.TimeSpan.TotalMilliseconds + 500; '
            'Start-Sleep -Milliseconds $d; '
            '$p.Close()'
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            logger.warning("Voice playback timed out")
        except Exception as e:
            logger.warning(f"Voice playback error: {e}")

    def _play_unix(self, filepath: str):
        """Play mp3 using ffplay or aplay fallback."""
        for cmd in [["ffplay", "-nodisp", "-autoexit", filepath],
                    ["mpv", "--no-video", filepath]]:
            try:
                subprocess.run(cmd, capture_output=True, timeout=60)
                return
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.warning(f"Playback with {cmd[0]} failed: {e}")
        logger.warning("No audio player found (tried ffplay, mpv)")
