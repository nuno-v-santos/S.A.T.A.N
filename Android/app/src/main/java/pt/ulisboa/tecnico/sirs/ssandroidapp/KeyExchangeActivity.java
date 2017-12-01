package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.Toast;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.security.InvalidAlgorithmParameterException;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.spec.RSAKeyGenParameterSpec;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging.BluetoothCommunication;

public class KeyExchangeActivity extends AppCompatActivity {
    Computer computer;
    BluetoothCommunication btCommunication;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connection);
        computer = (Computer) getIntent().getSerializableExtra(Constants.COMPUTER_OBJ);
        MyApplication app = (MyApplication) getApplicationContext();
        btCommunication = (BluetoothCommunication) app.getCommunicationInterface();

        //create key pair for Phone  FIXME : export this to security module
        KeyPair keyPair = null;
        PublicKey publicKey = null;
        PrivateKey privateKey = null;
        try {
            RSAKeyGenParameterSpec spec = new RSAKeyGenParameterSpec(Constants.RSA_KEY_SIZE, RSAKeyGenParameterSpec.F4);
            KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");
            keyGen.initialize(spec);
            keyPair = keyGen.generateKeyPair();
        } catch (InvalidAlgorithmParameterException e) {
            e.printStackTrace();
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }

        if(keyPair != null){
            publicKey = (PublicKey) keyPair.getPublic();
            privateKey = (PrivateKey) keyPair.getPrivate();
        }

        //send Phone public key encrypted with PC public key FIXME: export to security module
        //String PEMpublicKey = Base64.encodeToString(publicKey.getEncoded(), Base64.DEFAULT);

        //String PEMpublicKey = computer.getPublicPemFormat(publicKey);

        //btCommunication.sendMessage(PEMpublicKey.getBytes());
    }

    @Override
    public void onPause() { // FIXME NOT ON PAUSE, SHOULD BE WHEN INITIAL CONNECTION IS COMPLETED
        super.onPause();
        try {
            ObjectOutputStream oos = new ObjectOutputStream(this.openFileOutput(Constants.COMPUTER_OBJ_FILENAME, this.MODE_PRIVATE));
            oos.writeObject(computer);
            oos.close();
        } catch (IOException ie) {
            Toast.makeText(getApplicationContext(), R.string.IOException_write_obj_error_msg, Toast.LENGTH_LONG).show();
        }
    }
}
