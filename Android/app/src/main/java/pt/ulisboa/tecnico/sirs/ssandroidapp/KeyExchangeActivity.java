package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.security.Key;
import java.security.KeyPair;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.SecureRandom;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging.BluetoothCommunication;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.Encryption;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.KeyManagement;

public class KeyExchangeActivity extends AppCompatActivity {
    Computer computer;
    BluetoothCommunication btCommunication;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_key_exchange);
        computer = (Computer) getIntent().getSerializableExtra(Constants.COMPUTER_OBJ);
        MyApplication app = (MyApplication) getApplicationContext();
        btCommunication = (BluetoothCommunication) app.getCommunicationInterface();

        KeyManagement km = new KeyManagement();
        Encryption encryption = new Encryption();
        String password = getIntent().getStringExtra(Constants.PASSWORD_ID);

        TextView statusTV = findViewById(R.id.statusTV);
        ProgressBar progressBar = findViewById(R.id.progressBar);

        try {
            statusTV.setText(R.string.generating_pair);
            KeyPair keyPair = km.createAssymetricKeys(Constants.RSA_KEY_SIZE);
            Key computerPublicKey = computer.getPublicKey(this, password);
            PublicKey publicKey = keyPair.getPublic();
            PrivateKey privateKey = keyPair.getPrivate();

            // TEK Establishment
            statusTV.setText(R.string.tek_establishment);
            progressBar.setProgress(15);
            Key TEK = km.createSymmetricKey(Constants.AES_KEY_SIZE);
            byte[] encryptedTEK = encryption.RSAencrypt(TEK.getEncoded(), computerPublicKey);
            btCommunication.sendMessage(encryptedTEK);

            // Public Key dispatch [KEK]
            statusTV.setText(R.string.public_dispatch);
            progressBar.setProgress(30);
            SecureRandom random = new SecureRandom();
            byte[] ivTEK = new byte[16];
            random.nextBytes(ivTEK);

            String publicPEMKey = km.getKeyPEMFormat(publicKey);

            byte[] encryptedPublic = encryption.AESencrypt(publicPEMKey.getBytes(), TEK, "CBC", ivTEK);

            // iv || publicKey[TEK]
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            baos.write(ivTEK);
            baos.write(encryptedPublic);
            encryptedPublic = baos.toByteArray();

            btCommunication.sendMessage(encryptedPublic);

            // DEK and MEK generation
            statusTV.setText(R.string.dek_mek_establishment);
            progressBar.setProgress(45);
            Key DEK = km.createSymmetricKey(Constants.AES_KEY_SIZE);
            Key MEK = km.createSymmetricKey(Constants.AES_KEY_SIZE);
            byte[] ivMEK = new byte[16];
            random.nextBytes(ivMEK);
            random.nextBytes(ivTEK);

            // DEK(MEK)[TEK] Dispatch
            statusTV.setText(R.string.dek_mek_dispatch);
            progressBar.setProgress(60);
            byte[] encryptedDEK = encryption.AESencrypt(DEK.getEncoded(), MEK, "CBC", ivMEK);
            byte[] encryptedDEKMEK = encryption.AESencrypt(encryptedDEK, TEK, "CBC", ivTEK);

            // iv || DEK(MEK)[TEK]
            baos = new ByteArrayOutputStream();
            baos.write(ivTEK);
            baos.write(encryptedDEKMEK);
            encryptedDEKMEK = baos.toByteArray();

            btCommunication.sendMessage(encryptedDEKMEK);

            // DEK[TEK] Dispatch
            statusTV.setText(R.string.send_dek);
            progressBar.setProgress(75);
            random.nextBytes(ivTEK);
            encryptedDEK = encryption.AESencrypt(DEK.getEncoded(), TEK, "CBC", ivTEK);

            // iv || DEK[TEK]
            baos = new ByteArrayOutputStream();
            baos.write(ivTEK);
            baos.write(encryptedDEK);
            encryptedDEK = baos.toByteArray();

            btCommunication.sendMessage(encryptedDEK);

            btCommunication.close();

            // Key store
            statusTV.setText(R.string.key_storing);
            progressBar.setProgress(90);
            km.storeKey(this, publicKey, Constants.ANDROID_PUBLIC_KEY_ID, password);
            km.storeKey(this, privateKey, Constants.ANDROID_PRIVATE_KEY_ID, password);
            km.storeKey(this, MEK, Constants.ANDROID_MEK_ID, password);
            km.storeIV(this, ivMEK, Constants.ANDROID_MEK_IV_ID, password);

        } catch (Exception e) {
            e.printStackTrace();
            abort();
            return;
        }

        // Store computer object in device filesystem
        try {
            statusTV.setText(R.string.computer_storing);
            progressBar.setProgress(95);
            ObjectOutputStream oos = new ObjectOutputStream(this.openFileOutput(Constants.COMPUTER_OBJ_FILENAME, this.MODE_PRIVATE));
            oos.writeObject(computer);
            oos.close();
        } catch (IOException ie) {
            Toast.makeText(getApplicationContext(), R.string.IOException_write_obj_error_msg, Toast.LENGTH_LONG).show();
        }
        statusTV.setText(getResources().getString(R.string.pairing_completed, computer.getName()));
        progressBar.setProgress(100);

        Button button = findViewById(R.id.pairingEndButton);
        button.setVisibility(View.VISIBLE);
    }

    public void changeActivity2Main(View view) {
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
    }

    private void abort() {
        Toast.makeText(getApplicationContext(), R.string.error, Toast.LENGTH_LONG).show();
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
    }
}
