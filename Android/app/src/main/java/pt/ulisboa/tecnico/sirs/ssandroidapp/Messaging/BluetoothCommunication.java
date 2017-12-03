package pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging;

import android.app.Application;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.util.Log;

import java.io.IOException;
import java.io.Serializable;
import java.util.UUID;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Constants;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging.CommunicationInterface;

/**
 * Created by Nuno Santos on 30/11/2017.
 */

public class BluetoothCommunication implements CommunicationInterface{

    public BluetoothSocket btSocket;

    @Override
    public boolean connect(BluetoothDevice btDevice){

        try {
            btSocket = btDevice.createRfcommSocketToServiceRecord(UUID.fromString(Constants.DEFAULT_UUID));
        } catch (IOException e) {
            return false;
        }

        try {
            btSocket.connect();
        } catch(IOException e) {
            try {
                btSocket.close();
                return false;
            } catch(IOException close) {
                return false;
            }
        }
        return true;
    }

    @Override
    public void sendMessage(byte[] message) throws IOException {
        btSocket.getOutputStream().write(message);
    }

    @Override
    public byte[] receiveMessage() throws IOException {
        byte[] buffer = new byte[Constants.RECEIVER_BUFFER_SIZE];
        int bytes = btSocket.getInputStream().read(buffer);
        return buffer;
    }

    @Override
    public byte[] receiveMessage(int size) throws IOException {
        byte[] buffer = new byte[size];
        int bytes = btSocket.getInputStream().read(buffer);
        return buffer;
    }

    @Override
    public void close() {
        if (btSocket!=null)
            try {
                btSocket.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
    }
}
