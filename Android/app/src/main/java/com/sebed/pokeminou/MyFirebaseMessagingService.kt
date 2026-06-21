package com.sebed.pokeminou

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import java.net.HttpURLConnection
import java.net.URL

class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("FCM", "Nouveau token: $token")
        // Le backend envoie les messages sur le topic "all"
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        // Les données arrivent souvent dans la section 'data' si on envoie une image
        val catName = remoteMessage.data["cat_name"] ?: "Chat inconnu"
        val imageUrl = remoteMessage.data["image_url"]
        
        val title = remoteMessage.notification?.title ?: remoteMessage.data["title"] ?: "Minou Détecté!"
        val body = remoteMessage.notification?.body ?: remoteMessage.data["body"] ?: catName

        var bitmap: Bitmap? = null
        if (imageUrl != null) {
            try {
                val url = URL(imageUrl)
                val connection = url.openConnection() as HttpURLConnection
                connection.doInput = true
                connection.connect()
                val input = connection.inputStream
                bitmap = BitmapFactory.decodeStream(input)
            } catch (e: Exception) {
                Log.e("FCM", "Erreur téléchargement image", e)
            }
        }

        sendNotification(title, body, bitmap, catName, imageUrl)
    }

    private fun sendNotification(title: String, messageBody: String, image: Bitmap?, catName: String?, imageUrl: String?) {
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
        
        // C'est CRUCIAL : il faut remettre le payload dans l'intent manuel pour le mode Foreground !
        if (catName != null) intent.putExtra("cat_name", catName)
        if (imageUrl != null) intent.putExtra("image_url", imageUrl)
        
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val channelId = "pokeminou_alerts"
        val notificationBuilder = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(messageBody)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)

        if (image != null) {
            notificationBuilder.setLargeIcon(image)
            notificationBuilder.setStyle(
                NotificationCompat.BigPictureStyle()
                    .bigPicture(image)
                    .bigLargeIcon(null as Bitmap?)
            )
        }

        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Alertes PokeMinou",
                NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }

        notificationManager.notify(System.currentTimeMillis().toInt(), notificationBuilder.build())
    }
}
