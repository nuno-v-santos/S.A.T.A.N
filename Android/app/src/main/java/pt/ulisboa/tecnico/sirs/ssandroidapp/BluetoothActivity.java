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

    ArrayList<String> paired_devices_description = new ArrayList<>();
    ListView pairedDevicesList;
    ArrayList<String> discovered_devices_description = new ArrayList<>();
    ListView discoveredDevicesList;
    ArrayAdapter<String> pairedAdapter;
    ArrayAdapter<String> discoveredAdapter;
    BluetoothAdapter btAdapter;
    BluetoothCommunication btCommunication = new BluetoothCommunication();
    HashMap<String,BluetoothDevice> deviceMapping = new HashMap<>();
    Computer pc;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_bluetooth);

        btAdapter = BluetoothAdapter.getDefaultAdapter();

        pairedDevicesList = findViewById(R.id.paired_devices_list);
        discoveredDevicesList = findViewById(R.id.discovered_devices_list);

        pairedAdapter = new ArrayAdapter<>(this,
                                    android.R.layout.simple_selectable_list_item,
                                    paired_devices_description);
        pairedDevicesList.setAdapter(pairedAdapter);

        discoveredAdapter = new ArrayAdapter<>(this,
                android.R.layout.simple_selectable_list_item,
                discovered_devices_description);
        discoveredDevicesList.setAdapter(discoveredAdapter);

        //if the device doesnt have bluetooth, or it isnt enabled
        checkDeviceBluetooth();

        //set listener for the scan button
        scanButtonListener();

        //set listener for the items in the list of devices
        itemClickListener();
    }

    private void itemClickListener() {
        //if clicked on paired device
        pairedDevicesList.setOnItemClickListener(new AdapterView.OnItemClickListener(){
            @Override
            public void onItemClick(AdapterView<?> adapter,View v, int position, long id){
                //get the clicked device
                String clickedDevice = (String) adapter.getItemAtPosition(position);
                CreatePC(clickedDevice);  //create PC and set name and mac
                Connect2Device();
            }
        });

        //if clicked on discovered device
        discoveredDevicesList.setOnItemClickListener(new AdapterView.OnItemClickListener(){
            @Override
            public void onItemClick(AdapterView<?> adapter,View v, int position, long id){
                //get the clicked device
                String clickedDevice = (String) adapter.getItemAtPosition(position);
                CreatePC(clickedDevice);  //create PC and set name and mac
                Connect2Device();
            }
        });
    }

    private void scanButtonListener() {
        Switch scan = findViewById(R.id.scan_button);
        scan.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                IntentFilter filter = new IntentFilter(BluetoothDevice.ACTION_FOUND);
                if (isChecked) {
                    pairedAdapter.clear();
                    discoveredAdapter.clear();
                    //add the already paired devices
                    for (BluetoothDevice device : btAdapter.getBondedDevices()) {
                        paired_devices_description.add(device.getName() + " " + device.getAddress());
                        deviceMapping.put(device.getAddress(),device);
                        pairedAdapter.notifyDataSetChanged();
                    }
                    registerReceiver(mReceiver, filter);
                    btAdapter.startDiscovery();
                } else {
                    if (btAdapter.isDiscovering()) {
                        unregisterReceiver(mReceiver);
                        btAdapter.cancelDiscovery();
                    }
                }
            }
        });
    }

    private void checkDeviceBluetooth() {
        //If Phone doesnt have bluetooth
        if (btAdapter == null) {
            toast("Your phone does not support Bluetooth");
            Intent intent = new Intent(this, MainActivity.class);
            startActivity(intent);
        }

        //If bluetooth is not enabled
        if (!btAdapter.isEnabled()) {
            btAdapter.enable();
        }
    }

    //This discovers the devices nearby
    private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        // When discovery finds a device
        if (BluetoothDevice.ACTION_FOUND.equals(action)) {
            // Get the BluetoothDevice object from the Intent
            BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
            String new_device = device.getName() + " " + device.getAddress();
            if (!discovered_devices_description.contains(new_device)) {
                discovered_devices_description.add(new_device);
                deviceMapping.put(device.getAddress(),device);
                discoveredAdapter.notifyDataSetChanged();
            }
        }
        }
    };

    public void CreatePC(String clickedDevice) {
        String[] description = clickedDevice.split(" ");
        String chosen_mac = description[description.length - 1];
        String chosen_name = clickedDevice.replace(chosen_mac,"").trim();
        pc = new Computer();
        pc.setName(chosen_name);
        pc.setMac(chosen_mac);
    }

    public void Connect2Device() {
        boolean connected = btCommunication.connect(deviceMapping.get(pc.getMac()));

        if (connected) {
            //stop discovery
            if (btAdapter.isDiscovering()) {
                unregisterReceiver(mReceiver);
                btAdapter.cancelDiscovery();
            }

            //save btCommunication
            MyApplication app = (MyApplication) getApplicationContext();
            app.setCommunicationInterface(btCommunication);

            Intent intent = new Intent(getBaseContext(), QRScannerActivity.class);
            intent.putExtra(Constants.COMPUTER_OBJ, pc);
            intent.putExtra(Constants.PASSWORD_ID, getIntent().getStringExtra(Constants.PASSWORD_ID));
            startActivity(intent);
        } else {
            toast("Connection Failed. Try again.");
        }
    }

    public void toast(String m){
        Toast.makeText(getApplicationContext(), m, Toast.LENGTH_LONG).show();
    }
}
