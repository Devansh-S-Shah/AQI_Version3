package com.example.coughapp

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    private lateinit var recorder: AudioRecorderHelper
    private lateinit var classifier: TFLiteClassifier
    private var recordedBuffer = mutableListOf<Short>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnRecord = findViewById<Button>(R.id.btnRecord)
        val tvStatus = findViewById<TextView>(R.id.tvStatus)

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 1)
        }

        classifier = TFLiteClassifier(this)

        recorder = AudioRecorderHelper { buffer ->
            synchronized(recordedBuffer) {
                for (s in buffer) recordedBuffer.add(s)
            }
        }

        btnRecord.setOnClickListener {
            recordedBuffer.clear()
            tvStatus.text = "Recording... 2s"
            recorder.start()
            thread {
                Thread.sleep(2200)
                recorder.stop()
                runOnUiThread { tvStatus.text = "Processing..." }
                val pcmShorts: ShortArray
                synchronized(recordedBuffer) {
                    pcmShorts = recordedBuffer.toShortArray()
                }
                val floats = ShortToFloatConverter.shortToFloatArray(pcmShorts)
                val spec = SpectrogramUtil.computeLogMelSpectrogram(floats)
                val n_mels = spec.size
                val time_frames = spec[0].size
                val input = Array(1) { Array(n_mels) { Array(time_frames) { FloatArray(1) } } }
                for (i in 0 until n_mels) {
                    for (j in 0 until time_frames) {
                        input[0][i][j][0] = spec[i][j]
                    }
                }
                val out = classifier.runInference(input)
                val label = if (out[1] > out[0]) "Diseased" else "Healthy"
                runOnUiThread { tvStatus.text = "Result: $label" }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        classifier.close()
    }
}
