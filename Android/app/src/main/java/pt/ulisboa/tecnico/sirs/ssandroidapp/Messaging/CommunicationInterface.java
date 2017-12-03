package pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging;

import android.bluetooth.BluetoothDevice;

import java.io.IOException;

/**
 * Created by Nuno Santos on 30/11/2017.
 */

public interface CommunicationInterface {
    boolean connect(BluetoothDevice btDevice);
    void sendMessage(byte[] message) throws IOException;
    byte[] receiveMessage() throws IOException;
    byte[] receiveMessage(int size) throws IOException;
    void close();
}
