package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.app.Application;
import pt.ulisboa.tecnico.sirs.ssandroidapp.Messaging.CommunicationInterface;

/**
 * Created by Nuno Santos on 30/11/2017.
 */

public class MyApplication extends Application {

    private CommunicationInterface communicationInterface;

    public CommunicationInterface getCommunicationInterface() {
        return communicationInterface;
    }

    public void setCommunicationInterface(CommunicationInterface communicationInterface) {
        this.communicationInterface = communicationInterface;
    }
}
