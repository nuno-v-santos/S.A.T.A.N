package pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging;

import android.bluetooth.BluetoothDevice;

/**
 * Created by Nuno Santos on 30/11/2017.
 */

public interface CommunicationInterface {
    boolean connect(BluetoothDevice btDevice);
    void sendMessage(byte[] message);
    byte[] receiveMessage();
}
