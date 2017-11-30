package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.google.zxing.Result;

import java.sql.Connection;

import me.dm7.barcodescanner.zxing.ZXingScannerView;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging.BluetoothCommunication;

public class QRScannerActivity extends AppCompatActivity implements ZXingScannerView.ResultHandler {
    private ZXingScannerView zXingScannerView;
    private String qrMsg = "";
    private Computer computer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        computer = (Computer) getIntent().getSerializableExtra(Constants.COMPUTER_OBJ);
        zXingScannerView = new ZXingScannerView(getApplicationContext());
        setContentView(zXingScannerView);  // use zXing qrScanner layout
        zXingScannerView.setResultHandler(this);
        zXingScannerView.startCamera();
    }

    @Override
    protected void onPause() {
        super.onPause();
        zXingScannerView.stopCamera(); // when out of focus, stop camera
    }

    @Override
    protected void onResume() {
        super.onResume();
        zXingScannerView.resumeCameraPreview(this); // back to focus, setup qrReader
        zXingScannerView.startCamera();
    }

    @Override
    public void handleResult(Result result) {
        Toast.makeText(getApplicationContext(), R.string.qr_code_read_success_msg, Toast.LENGTH_SHORT).show(); // little popup saying qr read was a success
        zXingScannerView.stopCamera();
        setContentView(R.layout.activity_qrscanner); // change layout
        TextView tv = findViewById(R.id.qrMsgTV);
        qrMsg = result.getText();
        tv.setText(qrMsg); // add qr message to text view

        Button button = findViewById(R.id.doneButton);
        if (!validPublicKey(qrMsg)) {
            button.setEnabled(false);
            Toast.makeText(getApplicationContext(), R.string.invalid_public_key, Toast.LENGTH_SHORT).show();
        }
        else button.setEnabled(true);
    }

    private boolean validPublicKey(String msg) {
        String[] lines = msg.split("\\r?\\n");
        return lines[0].equals(Constants.RSA_PUBLIC_BEGIN) && lines[lines.length - 1].equals(Constants.RSA_PUBLIC_END);
    }

    public void changeActivityRepeat(View view) {
        retryQRScanner();
    }

    private void retryQRScanner(){
        setContentView(zXingScannerView);
        zXingScannerView.resumeCameraPreview(this);
        zXingScannerView.startCamera();
    }

    public void changeActivityCancel(View view) {
        Intent intent = new Intent(this, MainActivity.class); // go back to main activity
        startActivity(intent);
    }

    public void changeActivityDone(View view) {
        try {
            computer.setupPublicKey(this, qrMsg, Constants.SHARED_PREFERENCES_KEY); // FIXME ask user for a password to cypher/decypher the computers public key
        } catch (Exception e) { // invalid public key scanned, repeat
            Toast.makeText(getApplicationContext(), "Invalid public key scanned", Toast.LENGTH_LONG).show();
            retryQRScanner();
            return;
        }

        Intent intent = new Intent(this, KeyExchangeActivity.class);
        intent.putExtra(Constants.COMPUTER_OBJ, computer);
        startActivity(intent);
    }
}
