package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.security.PublicKey;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {
    Computer computer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void changeActivity2BluetoothPair(View view) {
        Intent intent = new Intent(this, BluetoothActivity.class);
        startActivity(intent);
    }

    public void changeActivity2Connection(View view){
        try {
            ObjectInputStream ois = new ObjectInputStream(this.openFileInput(Constants.COMPUTER_OBJ_FILENAME));
            computer = (Computer) ois.readObject();
            ois.close();
            if (computer == null)
                Toast.makeText(getApplicationContext(), "Dont have any paired computer", Toast.LENGTH_LONG).show();
            else{
                Intent intent = new Intent(this, ConnectionActivity.class);
                startActivity(intent);
            }
        } catch (IOException ie) {
            // pairing not done yet or filesystem error -> pairing phase needs to be done again
            Toast.makeText(getApplicationContext(), R.string.IOException_read_obj_error_msg, Toast.LENGTH_LONG).show();
        } catch (ClassNotFoundException ce) {
            // unable to get computer obj, pairing needs to be done again
            Toast.makeText(getApplicationContext(), R.string.ClassNotFoundException_error_msg, Toast.LENGTH_LONG).show();
        }
    }

}
