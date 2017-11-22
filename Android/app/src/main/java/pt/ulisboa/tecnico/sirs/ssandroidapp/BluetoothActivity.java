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
import android.widget.Toast;

import java.io.IOException;
import java.io.ObjectOutputStream;
import java.util.ArrayList;
import java.util.UUID;

public class BluetoothActivity extends AppCompatActivity {

    ArrayList<String> devices_description = new ArrayList<String>();
    ArrayAdapter<String> adapter;
    String chosen_name;
    String chosen_mac;
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
            alert("Not compatible", "Your phone does not support Bluetooth");
        }

        int REQUEST_ENABLE_BT = 1;
        //If bluetooth is not enabled, request to enable
        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }

        //if the user doesnt enable the bluetooth
        if (REQUEST_ENABLE_BT == 0){
            alert("Bluetooth not enabled", "Bluetooth needs to be enabled to continue pairing");
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
                        devices_description.add(device.getName() + " at " + device.getAddress());
                        adapter.notifyDataSetChanged();
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
                //Stop discovery
                unregisterReceiver(mReceiver);
                mBluetoothAdapter.cancelDiscovery();
                //get the clicked device
                String clickedDevice = (String) adapter.getItemAtPosition(position);
                chosen_name = clickedDevice.split(" ")[0];
                chosen_mac = clickedDevice.split(" ")[2];
                //create, fill, and serialize Computer
                Computer pc = new Computer();
                pc.setName(chosen_name);
                pc.setMac(chosen_mac);

                Intent intent = new Intent(getBaseContext(), QRScannerActivity.class);
                intent.putExtra(Constants.COMPUTER_OBJ, pc);
                startActivity(intent);
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
            String new_device = device.getName() + " at " + device.getAddress();
            if (!devices_description.contains(new_device)) {
                devices_description.add(new_device);
                adapter.notifyDataSetChanged();
            }
        }
        }
    };

    public void alert(String title, String text){
        new AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(text)
            .setPositiveButton("Exit", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int which) {
                    System.exit(0);
                }
            })
            .setIcon(android.R.drawable.ic_dialog_alert)
            .show();
    }
}
