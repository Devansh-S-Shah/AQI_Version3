package com.example.coughapp

import android.content.Context
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import kotlin.random.Random
import android.util.Log

class TFLiteClassifier(context: Context, modelPath: String = "cough_model.tflite") {
    private var interpreter: Interpreter? = null
    private var hasModel = false

    init {
        try {
            val afd = context.assets.openFd(modelPath)
            val input = FileInputStream(afd.fileDescriptor)
            val channel = input.channel
            val start = afd.startOffset
            val len = afd.length
            val mb = channel.map(FileChannel.MapMode.READ_ONLY, start, len)
            interpreter = Interpreter(mb)
            hasModel = true
        } catch (e: Exception) {
            Log.i("TFLiteClassifier", "No model in assets; using simulated random outputs for demo.")
            hasModel = false
        }
    }

    fun runInference(floatInput: Array<Array<Array<FloatArray>>>): FloatArray {
        return if (hasModel && interpreter != null) {
            val output = Array(1) { FloatArray(2) }
            interpreter!!.run(floatInput, output)
            // add small randomness to outputs
            val r = Random.nextFloat() * 0.2f - 0.1f
            output[0][0] = (output[0][0] + r).coerceIn(0.0f, 1.0f)
            output[0][1] = (output[0][1] - r).coerceIn(0.0f, 1.0f)
            val s = output[0][0] + output[0][1] + 1e-6f
            output[0][0] /= s; output[0][1] /= s
            output[0]
        } else {
            // Simulate randomized softmax-like output
            val a = Random.nextFloat().toFloat()
            val b = Random.nextFloat().toFloat()
            val s = a + b + 1e-6f
            floatArrayOf(a / s, b / s)
        }
    }

    fun close() { interpreter?.close() }
}
