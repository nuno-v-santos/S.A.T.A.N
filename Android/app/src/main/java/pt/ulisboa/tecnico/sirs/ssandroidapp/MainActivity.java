package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // FIXME store permanently the public key
        String publicKey = getIntent().getStringExtra(QRScannerActivity.QR_MSG);
        if (publicKey != null) {
            TextView tv = findViewById(R.id.publicKeyTV);
            tv.setText(publicKey);
            tv.setVisibility(View.VISIBLE);
        }
        ////////////////////////////////////////////
    }

    public void changeActivity2QRScanner(View view) {
        Intent intent = new Intent(this, QRScannerActivity.class);
        startActivity(intent);
    }

    public void changeActivity2BluetoothPair(View view) {
        Intent intent = new Intent(this, BluetoothActivity.class);
        startActivity(intent);
    }
}
