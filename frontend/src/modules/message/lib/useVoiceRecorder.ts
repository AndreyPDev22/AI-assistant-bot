import { ref, onBeforeUnmount, type Ref } from 'vue';
import type { MessageFile } from '../model';

export type VolumeLevel = 1 | 2 | 3 | 4 | 5;

const VOLUME_THRESHOLDS = [0.03, 0.08, 0.15, 0.25];
const MIN_VOLUME_LEVEL: VolumeLevel = 1;
const ANALYSER_FFT_SIZE = 256;
const BYTE_SILENCE_VALUE = 128;
const MIN_VISIBLE_BARS = 1;
const VOLUME_TICK_INTERVAL_MS = 100;

export function useVoiceRecorder(
  volumesContainer: Readonly<Ref<HTMLElement | null>>,
  onRecorded: (file: MessageFile) => void,
) {
  let mediaRecorder: MediaRecorder | null = null;
  let mediaStream: MediaStream | null = null;
  let chunks: Blob[] = [];
  let audioContext: AudioContext | null = null;
  let volumeIntervalId = 0;

  const isRecording = ref(false);
  const volumeLevelsHistory = ref<VolumeLevel[]>([]);

  onBeforeUnmount(() => {
    if (mediaRecorder) {
      mediaRecorder.onstop = null;
    }

    stopRecording();
    releaseMicrophone();
  });

  async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia) {
      console.error('Запись звука недоступна: нужен HTTPS или localhost');
      return;
    }

    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (error) {
      console.error('Не удалось получить доступ к микрофону', error);
      return;
    }

    chunks = [];
    mediaRecorder = new MediaRecorder(mediaStream);

    mediaRecorder.ondataavailable = (event: BlobEvent) => chunks.push(event.data);
    mediaRecorder.onstop = onRecordingStop;

    mediaRecorder.start();
    startVolumeMeter(mediaStream);

    isRecording.value = true;
  }

  function stopRecording() {
    if (mediaRecorder?.state === 'recording') {
      mediaRecorder.stop();
    }

    stopVolumeMeter();

    isRecording.value = false;
  }

  function toggleRecording() {
    if (isRecording.value) {
      stopRecording();
    } else {
      startRecording();
    }
  }

  function onRecordingStop() {
    const mimeType = mediaRecorder?.mimeType ?? 'audio/webm';
    const blob = new Blob(chunks, { type: mimeType });
    const extension = mimeType.split('/')[1]?.split(';')[0] ?? 'webm';

    onRecorded({
      id: crypto.randomUUID(),
      name: `voice-message.${extension}`,
      url: URL.createObjectURL(blob),
    });

    releaseMicrophone();
  }

  function releaseMicrophone() {
    stopVolumeMeter();

    mediaStream?.getTracks().forEach((track) => track.stop());
    mediaStream = null;
    mediaRecorder = null;
  }

  function startVolumeMeter(stream: MediaStream) {
    audioContext = new AudioContext();
    audioContext.resume();

    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = ANALYSER_FFT_SIZE;
    source.connect(analyser);

    const data = new Uint8Array(analyser.fftSize);

    const tick = () => {
      analyser.getByteTimeDomainData(data);

      let sum = 0;
      for (const value of data) {
        const deviation = (value - BYTE_SILENCE_VALUE) / BYTE_SILENCE_VALUE;
        sum += deviation * deviation;
      }
      const rms = Math.sqrt(sum / data.length);

      const index = VOLUME_THRESHOLDS.findIndex((threshold) => rms < threshold);
      const maxVolumeLevel = VOLUME_THRESHOLDS.length + MIN_VOLUME_LEVEL;
      const volumeLevel = (index === -1 ? maxVolumeLevel : index + MIN_VOLUME_LEVEL) as VolumeLevel;

      volumeLevelsHistory.value.push(volumeLevel);
      trimVolumeHistory();
    };

    tick();

    volumeIntervalId = setInterval(tick, VOLUME_TICK_INTERVAL_MS);
  }

  function trimVolumeHistory() {
    const container = volumesContainer.value;
    const bar = container?.firstElementChild;

    if (!container || !bar) {
      return;
    }

    const gap = parseFloat(getComputedStyle(container).columnGap) || 0;
    const barWidth = bar.getBoundingClientRect().width;
    const maxBars = Math.max(
      MIN_VISIBLE_BARS,
      Math.floor((container.clientWidth + gap) / (barWidth + gap)),
    );

    const excess = volumeLevelsHistory.value.length - maxBars;

    if (excess > 0) {
      volumeLevelsHistory.value.splice(0, excess);
    }
  }

  function stopVolumeMeter() {
    clearInterval(volumeIntervalId);
    audioContext?.close();
    audioContext = null;
    volumeLevelsHistory.value = [];
  }

  return { isRecording, volumeLevelsHistory, toggleRecording };
}
