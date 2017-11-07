package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.google.zxing.Result;

import me.dm7.barcodescanner.zxing.ZXingScannerView;

public class QRScannerActivity extends AppCompatActivity implements ZXingScannerView.ResultHandler {
    public static final String QR_MSG = "pt.ulisboa.tecnico.sirs.ssandroidapp.QR_MSG";
    private static final String READ_SUCCESS = "QR successfully read!";
    private ZXingScannerView zXingScannerView;
    private String qrMsg = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
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
        Toast.makeText(getApplicationContext(), READ_SUCCESS, Toast.LENGTH_SHORT).show(); // little popup saying qr read was a success
        zXingScannerView.stopCamera();
        setContentView(R.layout.activity_qrscanner); // change layout
        TextView tv = findViewById(R.id.qrMsgTV);
        qrMsg = result.getText();
        // FIXME check if valid qr message
        tv.setText(qrMsg); // add qr message to text view
    }

    public void changeActivityRepeat(View view) {
        setContentView(zXingScannerView);
        zXingScannerView.resumeCameraPreview(this);
        zXingScannerView.startCamera();
    }

    public void changeActivityCancel(View view) {
        Intent intent = new Intent(this, MainActivity.class); // go back to main activity
        startActivity(intent);
    }

    public void changeActivityDone(View view) {
        Intent intent = new Intent(this, MainActivity.class);
        // FIXME qrMsg should be like [computer_id]:[public_key]
        // FIXME only accept valid qrMsg and send Computer class to main activity
        intent.putExtra(QR_MSG, qrMsg); // send qr msg to main activity
        startActivity(intent);
    }
}
