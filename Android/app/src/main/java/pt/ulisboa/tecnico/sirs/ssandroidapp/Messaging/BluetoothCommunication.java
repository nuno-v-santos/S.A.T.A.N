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
    public void sendMessage(byte[] message) {
        try {
            btSocket.getOutputStream().write(message);
        } catch (IOException e) {
            Log.d("Failed_Write", "Could not write to socket.");
        }

    }

    @Override
    public byte[] receiveMessage() {
        byte[] buffer = new byte[Constants.RECEIVER_BUFFER_SIZE];
        try {
            int bytes = btSocket.getInputStream().read(buffer);
        } catch (IOException e) {
            Log.d("Failed_Read", "Could not read from socket.");
        }
        return buffer;
    }
}
