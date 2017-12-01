package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Context;
import android.util.Base64;

import java.io.Serializable;
import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Security.KeyManagement;

/**
 * Created by Guilherme on 07/11/2017.
 */

public class Computer implements Serializable {
    private String name = "default"; // bluetooth name
    private String mac = "00:00:00:00:00:00";  //bluetooth mac

    public void setName(String name) {
        this.name = name;
    }
    public void setMac(String mac) {
        this.mac = mac;
    }

    public String getName() { return name; }
    public String getMac() { return mac; }

    public void setupPublicKey(Context context, String publicKey, String password) throws InvalidKeySpecException, NoSuchAlgorithmException {
        KeyManagement km = new KeyManagement();
        PublicKey pk = km.generatePublicKeyFromPEM(publicKey);
        km.storeKey(context, pk, Constants.COMPUTER_PUBLIC_KEY_ID, password);
    }

    public PublicKey getPublicKey(Context context, String password) throws InvalidKeySpecException, NoSuchAlgorithmException {
        KeyManagement km = new KeyManagement();
        return (PublicKey) km.loadKey(context, Constants.COMPUTER_PUBLIC_KEY_ID, password);
    }
}
