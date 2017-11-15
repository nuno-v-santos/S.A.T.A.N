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
    private ZXingScannerView zXingScannerView;
    private String qrMsg = "";
    private Computer computer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        computer = (Computer) savedInstanceState.getSerializable(Constants.COMPUTER_OBJ); // gets computer obj from BluetoothActivity

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
        try {
            computer.setupPublicKey(qrMsg);
        } catch (Exception e) { // invalid public key scanned, repeat
            Toast.makeText(getApplicationContext(), R.string.qr_code_read_success_msg, Toast.LENGTH_LONG).show();
            setContentView(zXingScannerView);
            zXingScannerView.resumeCameraPreview(this);
            zXingScannerView.startCamera();
            return;
        }

        Intent intent = new Intent(this, MainActivity.class);

        Bundle b = new Bundle();
        b.putSerializable(Constants.COMPUTER_OBJ, computer);

        intent.putExtras(b);
        startActivity(intent);
    }
}
