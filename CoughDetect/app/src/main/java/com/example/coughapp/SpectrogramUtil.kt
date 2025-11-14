package com.example.coughapp

object SpectrogramUtil {
    fun computeLogMelSpectrogram(pcm: FloatArray, sampleRate: Int = 16000, nMels: Int = 64, hopLength: Int = 256): Array<FloatArray> {
        val frameLen = 1024
        val frames = 1 + (pcm.size - frameLen).coerceAtLeast(0) / hopLength
        val safeFrames = if (frames > 0) frames else 128
        val out = Array(nMels) { FloatArray(safeFrames) }
        for (j in 0 until safeFrames) {
            var sum = 0.0f
            val start = j * hopLength
            val end = (start + frameLen).coerceAtMost(pcm.size)
            for (k in start until end) sum += kotlin.math.abs(pcm[k])
            val energy = if (end>start) sum / (end-start) else 0.0f
            for (i in 0 until nMels) {
                out[i][j] = (energy * (1.0f - i.toFloat()/nMels)).toFloat()
            }
        }
        return out
    }
}

object ShortToFloatConverter {
    fun shortToFloatArray(shorts: ShortArray): FloatArray {
        val out = FloatArray(shorts.size)
        for (i in shorts.indices) out[i] = shorts[i] / 32768.0f
        return out
    }
}
