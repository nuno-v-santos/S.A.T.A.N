package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.security.PublicKey;
import java.util.UUID;

public class ConnectionActivity extends AppCompatActivity {
    Computer computer;
    BluetoothAdapter mBluetoothAdapter;
    BluetoothSocket btSocket;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connection);
        computer = (Computer) getIntent().getSerializableExtra(Constants.COMPUTER_OBJ);

        // shows current paired computer name onscreen if exists
        if (computer != null) {
            TextView tv = findViewById(R.id.statusTV);
            tv.setVisibility(View.VISIBLE);
            tv.setText("Trying to connect to paired device");
            boolean connected = connect();
            if (connected)
                tv.setText( "Connection completed. You are connected with " + computer.getName());
            else
                tv.setText("Failed to connect to paired device");
        }
    }

    @Override
    public void onPause() {
        super.onPause();
        try {
            ObjectOutputStream oos = new ObjectOutputStream(this.openFileOutput(Constants.COMPUTER_OBJ_FILENAME, this.MODE_PRIVATE));
            oos.writeObject(computer);
            oos.close();
        } catch (IOException ie) {
            Toast.makeText(getApplicationContext(), R.string.IOException_write_obj_error_msg, Toast.LENGTH_LONG).show();
        }
    }

    public boolean connect(){
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        BluetoothDevice btDevice = null;
        //search for device
        for (BluetoothDevice device : mBluetoothAdapter.getBondedDevices()) {
            if (device.getAddress().equals(computer.getMac())){
                btDevice = device;
                break;
            }
        }
        try {
            //create socket
            btSocket = btDevice.createRfcommSocketToServiceRecord(UUID.fromString(Constants.DEFAULT_UUID));
        } catch (IOException e) {
            Toast.makeText(getApplicationContext(), "Failed to create socket", Toast.LENGTH_LONG).show();
            return false;
        }

        try {
            btSocket.connect();
        } catch(IOException e) {
            Toast.makeText(getApplicationContext(), "Failed to connect to PC", Toast.LENGTH_LONG).show();
            try {
                btSocket.close();
                return false;
            } catch(IOException close) {
                Toast.makeText(getApplicationContext(), "Failed to close socket", Toast.LENGTH_LONG).show();
                return false;
            }
        }


        //TODO: Send our public key to the PC

        //TODO: Receive TEK (aka the session key) from the PC

        //Code to test connection
        /*try {
            String a = "Hello World";
            btSocket.getOutputStream().write(a.getBytes());
        } catch (IOException e) {
            Log.d("Failed_Write", "Could not write to socket.");
            return false;
        }
        try {
            byte[] buffer = new byte[1024];
            int bytes = btSocket.getInputStream().read(buffer);
            String readMessage = new String(buffer, 0, bytes);
            Log.d("Thomas message", readMessage);
        } catch (IOException e) {
            Log.d("Failed_Read", "Could not read from socket.");
            return false;
        }*/
        return true;
    }
}
