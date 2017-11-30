package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.CompoundButton;
import android.widget.ListView;
import android.widget.Switch;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Dictionary;
import java.util.HashMap;
import java.util.Map;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging.BluetoothCommunication;

public class BluetoothActivity extends AppCompatActivity {

    ArrayList<String> devices_description = new ArrayList<String>();
    ArrayAdapter<String> adapter;
    BluetoothAdapter mBluetoothAdapter;
    BluetoothCommunication btCommunication = new BluetoothCommunication();
    HashMap<String,BluetoothDevice> deviceMapping = new HashMap<String, BluetoothDevice>();
    Computer pc;

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
            Toast.makeText(getApplicationContext(), "Your phone does not support BluetoothCommunication", Toast.LENGTH_LONG).show();
            Intent intent = new Intent(this, MainActivity.class);
            startActivity(intent);
        }

        int REQUEST_ENABLE_BT = 1;
        //If bluetooth is not enabled, request to enable
        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }

        //if the user doesnt enable the bluetooth
        if (REQUEST_ENABLE_BT == 0){
            Toast.makeText(getApplicationContext(), "BluetoothCommunication needs to be enabled to continue pairing", Toast.LENGTH_LONG).show();
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
                        deviceMapping.put(device.getAddress(),device);
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
                try {
                    unregisterReceiver(mReceiver);
                    mBluetoothAdapter.cancelDiscovery();
                    //get the clicked device
                    String clickedDevice = (String) adapter.getItemAtPosition(position);
                    CreatePC(clickedDevice);  //create PC and set name and mac
                    Connect2Device();
                } catch (IllegalArgumentException e){
                    Toast.makeText(getApplicationContext(), "Connection Failed. Try again.", Toast.LENGTH_LONG).show();
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
            String new_device = device.getName() + " at " + device.getAddress();
            if (!devices_description.contains(new_device)) {
                devices_description.add(new_device);
                deviceMapping.put(device.getName(),device);
                adapter.notifyDataSetChanged();
            }
        }
        }
    };

    public void CreatePC(String clickedDevice) {
        String chosen_name = clickedDevice.split(" ")[0];
        String chosen_mac = clickedDevice.split(" ")[2];
        pc = new Computer();
        pc.setName(chosen_name);
        pc.setMac(chosen_mac);
    }

    public void Connect2Device() {
        boolean connected = btCommunication.connect(deviceMapping.get(pc.getMac()));

        if (connected) {
            Intent intent = new Intent(getBaseContext(), QRScannerActivity.class);
            intent.putExtra(Constants.COMPUTER_OBJ, pc);
            intent.putExtra(Constants.PASSWORD_ID, getIntent().getStringExtra(Constants.PASSWORD_ID));
            MyApplication app = (MyApplication) getApplicationContext();
            app.setCommunicationInterface(btCommunication);
            startActivity(intent);
        } else {
            Toast.makeText(getApplicationContext(), "Connection Failed. Try again.", Toast.LENGTH_LONG).show();
        }
    }
}
