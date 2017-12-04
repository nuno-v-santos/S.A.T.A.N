package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.security.Key;
import java.security.SecureRandom;
import java.util.Arrays;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging.BluetoothCommunication;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.Encryption;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.KeyManagement;

public class ConnectionActivity extends AppCompatActivity {
    BluetoothAdapter btAdapter;
    BluetoothCommunication bComm;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connection);

        KeyManagement km = new KeyManagement();
        Encryption en = new Encryption();
        String password = getIntent().getStringExtra(Constants.PASSWORD_ID);
        Computer computer = (Computer) getIntent().getSerializableExtra(Constants.COMPUTER_OBJ);
        TextView statusView = findViewById(R.id.connectionStatusTV);

        // Bluetooth connection
        statusView.setText(R.string.bluetooth_connection_status);
        btAdapter = BluetoothAdapter.getDefaultAdapter();
        if (!checkDeviceBluetooth()) {
            Toast.makeText(getApplicationContext(), R.string.bluetooth_error, Toast.LENGTH_LONG).show();
            abort();
            return;
        }
        bComm = new BluetoothCommunication();
        BluetoothDevice blueDvc = getComputerBluetoothDevice(computer.getMac());

        if (blueDvc == null) {
            Toast.makeText(getApplicationContext(), R.string.bluetooth_not_bound_error, Toast.LENGTH_LONG).show();
            abort();
            return;
        }

        if (!bComm.connect(blueDvc))
            Toast.makeText(getApplicationContext(), R.string.bluetooth_connection_error, Toast.LENGTH_SHORT).show();

        try {
            // TEK Establishment
            statusView.setText(R.string.tek_establishment);
            byte[] encryptedTEK = bComm.receiveMessage(256);
            Key privateKey = km.loadKey(this, Constants.ANDROID_PRIVATE_KEY_ID, password);
            byte[] encodedTEK = en.RSAdecrypt(encryptedTEK, privateKey);
            Key TEK = km.createSymmetricKey(encodedTEK);

            // Receive DEK(MEK) from Computer
            statusView.setText(R.string.wait_dek_mek);
            byte[] encryptedDEKMEK = bComm.receiveMessage(80);
            byte[] encryptedDEKMEKiv = Arrays.copyOfRange(encryptedDEKMEK, 0, 16);
            encryptedDEKMEK = Arrays.copyOfRange(encryptedDEKMEK, 16, encryptedDEKMEK.length);
            byte[] encodedDEKMEK = en.AESEAXdecrypt(encryptedDEKMEK, TEK, encryptedDEKMEKiv);

            // DEK retrieve and dispatch
            statusView.setText(R.string.send_dek);
            Key MEK = km.loadKey(this, Constants.ANDROID_MEK_ID, password);
            SecureRandom random = new SecureRandom();
            byte[] ivTEK = new byte[16];
            random.nextBytes(ivTEK);
            byte[] ivMEK = km.loadIV(this, Constants.ANDROID_MEK_IV_ID, password);
            byte[] encodedDEK = en.AESEAXdecrypt(encodedDEKMEK, MEK, ivMEK);
            byte[] encryptedDEK = en.AESEAXencrypt(encodedDEK, TEK, ivTEK);

            // iv || DEK[TEK]
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            baos.write(ivTEK);
            baos.write(encryptedDEK);
            encryptedDEK = baos.toByteArray();
            bComm.sendMessage(encryptedDEK);

            // heartbeat
            statusView.setText(R.string.pinging_computer);
            MyApplication app = (MyApplication) getApplicationContext();
            app.setCommunicationInterface(bComm);
            Intent intent = new Intent(this, HeartbeatService.class);
            HeartbeatService.TEK = TEK;
            startService(intent);

        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(getApplicationContext(), R.string.error, Toast.LENGTH_LONG).show();
            abort();
            return;
        }
    }

    private boolean checkDeviceBluetooth() {
        //If Phone doesnt have bluetooth
        if (btAdapter == null)
            return false;

        //If bluetooth is not enabled
        else if (!btAdapter.isEnabled())
            btAdapter.enable();
        return true;
    }

    private BluetoothDevice getComputerBluetoothDevice(String MAC) {
        // search for computer bluetooth device on bonded devices only
        for (BluetoothDevice device : btAdapter.getBondedDevices()) {
            if (device.getAddress().equals(MAC))
                return device;
        }
        return null;
    }

    private void abort() {
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
    }

    public void connectionDone(View view) {
        HeartbeatService.shouldContinue = false;
        bComm.close();
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
    }
}