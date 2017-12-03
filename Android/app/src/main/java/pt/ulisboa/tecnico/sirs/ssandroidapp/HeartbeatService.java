package pt.ulisboa.tecnico.sirs.ssandroidapp;


import android.app.IntentService;
import android.bluetooth.BluetoothDevice;
import android.content.Intent;
import android.os.Handler;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.nio.ByteBuffer;
import java.security.Key;
import java.security.SecureRandom;
import java.util.HashSet;
import java.util.Random;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging.BluetoothCommunication;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.Encryption;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.KeyManagement;

public class HeartbeatService extends IntentService {

    Handler mHandler;
    public static volatile boolean shouldContinue = true;
    public static volatile Key TEK;

    public HeartbeatService() {
        super("HeartbeatService");
    }

    @Override
    public void onCreate() {
        super.onCreate();
        mHandler = new Handler();
        shouldContinue = true;
    }

    /**
     * The IntentService calls this method from the default worker thread with
     * the intent that started the service. When this method returns, IntentService
     * stops the service, as appropriate.
     */
    @Override
    protected void onHandleIntent(Intent intent) {
        toast("STATOOO"); // FIXME remove
        MyApplication app = (MyApplication) getApplicationContext();
        BluetoothCommunication bComm = (BluetoothCommunication) app.getCommunicationInterface();
        Encryption en = new Encryption();
        HashSet<Integer> nounceSet = new HashSet<>();
        Random nounceGen = new Random();
        SecureRandom ivGen = new SecureRandom();

        try {
            while (shouldContinue) {
                toast("Pinging");

                byte[] ivTEK = new byte[16];
                ivGen.nextBytes(ivTEK);

                int nounce = nounceGen.nextInt();
                while (nounceSet.contains(nounce))
                    nounce = nounceGen.nextInt();
                nounceSet.add(nounce);

                byte[] encodedNounce = ByteBuffer.allocate(4).putInt(nounce).array();
                byte[] encryptedNounce = en.AESencrypt(encodedNounce, TEK, "CBC", ivTEK);

                // iv || nounce[TEK]
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                baos.write(ivTEK);
                baos.write(encryptedNounce);
                encryptedNounce = baos.toByteArray();
                bComm.sendMessage(encryptedNounce);

                Thread.sleep(Constants.HEARTBEAT_DELAY);            }
        } catch (Exception e) {
            toast("Error");
            e.printStackTrace();
            return;
        }

        toast("No more pinging");
    }

    private void toast(final String msg) {
        mHandler.post(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(HeartbeatService.this, msg, Toast.LENGTH_SHORT).show();
            }
        });
    }
}