package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.CompoundButton;
import android.widget.ListView;
import android.widget.Switch;

import java.io.IOException;
import java.util.ArrayList;
import java.util.UUID;

public class BluetoothActivity extends AppCompatActivity {

    ArrayList<BluetoothDevice> devices = new ArrayList<BluetoothDevice>();
    ArrayList<String> devices_description = new ArrayList<String>();
    ArrayAdapter<String> adapter;
    BluetoothDevice chosen_device;
    BluetoothSocket btSocket;
    BluetoothAdapter mBluetoothAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

        ListView list = (ListView) findViewById(R.id.devices_list);

        adapter = new ArrayAdapter<String>(this, android.R.layout.simple_selectable_list_item, devices_description);
        list.setAdapter(adapter);

        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

        //if the device doesnt have bluetooth
        if (mBluetoothAdapter == null) {
            new AlertDialog.Builder(this)
                    .setTitle("Not compatible")
                    .setMessage("Your phone does not support Bluetooth")
                    .setPositiveButton("Exit", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                            System.exit(0);
                        }
                    })
                    .setIcon(android.R.drawable.ic_dialog_alert)
                    .show();
        }

        int REQUEST_ENABLE_BT = 1;
        //If bluetooth is not enabled, request to enable
        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }

        //if the user doesnt enable the bluetooth
        if (REQUEST_ENABLE_BT == 0){
            Intent intent = new Intent(this, MainActivity.class);
            startActivity(intent);
        }

        //set listener for the scan button
        Switch scan = (Switch) findViewById(R.id.scan_button);
        scan.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
            IntentFilter filter = new IntentFilter(BluetoothDevice.ACTION_FOUND);
            if (isChecked) {
                adapter.clear();
                //add the already paired devices
                for (BluetoothDevice device : mBluetoothAdapter.getBondedDevices()) {
                    if (!devices.contains(device)) {
                        devices.add(device);
                        devices_description.add(device.getName() + " at " + device.getAddress());
                        adapter.notifyDataSetChanged();
                    }
                }
                registerReceiver(mReceiver, filter);
                //find new devices
                mBluetoothAdapter.startDiscovery();
            } else {
                unregisterReceiver(mReceiver);
                mBluetoothAdapter.cancelDiscovery();
            }
            }
        });

        //set listener for the items in the list of devices
        list.setOnItemClickListener(new AdapterView.OnItemClickListener(){
            @Override
            public void onItemClick(AdapterView<?> adapter,View v, int position, long id){
                String clickedDevice = (String) adapter.getItemAtPosition(position);
                for (BluetoothDevice d : devices){
                    if (d.getName().equals(clickedDevice.split(" ")[0])) {
                        chosen_device = d;
                        break;
                    }
                }
                boolean connected = connect();  //try to connect to chosen device
                if (connected) {
                    Intent intent = new Intent(getBaseContext(), QRScannerActivity.class);
                    startActivity(intent);
                } else {
                    Intent intent = new Intent(getBaseContext(), MainActivity.class);
                    startActivity(intent);
                }
            }
        });

    }

    //This discovers the devices nearby
    private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        // When discovery finds a device
        if (BluetoothDevice.ACTION_FOUND.equals(action)) {
            // Get the BluetoothDevice object from the Intent
            BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
            if (!devices.contains(device)) {
                devices.add(device);
                devices_description.add(device.getName() + " at " + device.getAddress());
                adapter.notifyDataSetChanged();
            }
        }
        }
    };

    public boolean connect(){
        try {
            //create socket
            btSocket = chosen_device.createRfcommSocketToServiceRecord(UUID.fromString("94f39d29-7d6d-437d-973b-fba39e49d4ee"));
        } catch (IOException e) {
            Log.d("Socket_Creation","Could not create socket.");
            return false;
        }

        try {
            btSocket.connect();
        } catch(IOException e) {
            Log.d("Connection_Failed","Could not connect to device.");
            try {
                btSocket.close();
                return false;
            } catch(IOException close) {
                Log.d("Failed_Close", "Could not close connection");
                return false;
            }
        }

        //Code to test connection
        /*
        try {
            btSocket.getOutputStream().write("City of stars".getBytes());
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
