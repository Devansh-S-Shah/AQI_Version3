package com.example.coughapp

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import kotlin.concurrent.thread

class AudioRecorderHelper(val sampleRate: Int = 16000, val onBuffer: (ShortArray) -> Unit) {
    private val bufferSize = AudioRecord.getMinBufferSize(sampleRate,
        AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
    private var recorder: AudioRecord? = null
    private var running = false

    fun start() {
        recorder = AudioRecord(MediaRecorder.AudioSource.MIC, sampleRate,
            AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, bufferSize)
        recorder?.startRecording()
        running = true
        thread {
            val buffer = ShortArray(bufferSize)
            while (running) {
                val read = recorder?.read(buffer, 0, buffer.size) ?: 0
                if (read > 0) {
                    onBuffer(buffer.copyOf(read))
                }
            }
        }
    }

    fun stop() {
        running = false
        recorder?.stop()
        recorder?.release()
        recorder = null
    }
}
