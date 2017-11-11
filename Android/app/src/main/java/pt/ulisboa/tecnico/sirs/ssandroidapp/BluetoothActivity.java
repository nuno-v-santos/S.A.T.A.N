package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.CompoundButton;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.ToggleButton;

import java.util.ArrayList;
import java.util.Set;

public class BluetoothActivity extends AppCompatActivity {

    ArrayList<String> devices = new ArrayList<String>();
    ArrayAdapter<String> adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

        ListView list = (ListView) findViewById(R.id.devices_list);

        adapter = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_item, devices);
        list.setAdapter(adapter);

        final BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (mBluetoothAdapter == null) {
            //if the device doesnt have bluetooth
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
        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }

        if (REQUEST_ENABLE_BT == 0){
            //if the user doesnt enable the bluetooth
            Intent intent = new Intent(this, MainActivity.class);
            startActivity(intent);
        }

        ToggleButton scan = (ToggleButton) findViewById(R.id.scan_button);
        scan.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                IntentFilter filter = new IntentFilter(BluetoothDevice.ACTION_FOUND);
                if (isChecked) {
                    adapter.clear();
                    registerReceiver(mReceiver, filter);
                    mBluetoothAdapter.startDiscovery();
                } else {
                    unregisterReceiver(mReceiver);
                    mBluetoothAdapter.cancelDiscovery();
                }
            }
        });
    }

    // Create a BroadcastReceiver for ACTION_FOUND
    private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            // When discovery finds a device
            if (BluetoothDevice.ACTION_FOUND.equals(action)) {
                // Get the BluetoothDevice object from the Intent
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                // Add the name and address to an array adapter to show in a ListView
                String device_description = device.getName() + " at " + device.getAddress();
                if (!devices.contains(device_description)) {
                    devices.add(device_description);
                    adapter.notifyDataSetChanged();
                }
            }
        }
    };

    public void changeNextActivity(View view) {
        //for now the activity after the bluetooth is the main
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
    }
}
