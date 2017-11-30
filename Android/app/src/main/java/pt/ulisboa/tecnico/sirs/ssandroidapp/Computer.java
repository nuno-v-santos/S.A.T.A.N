package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Context;
import android.util.Base64;

import java.io.Serializable;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.spec.X509EncodedKeySpec;

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


    // FIXME EXTRACT METHOD
    public void setupPublicKey(Context context, String publicKey, String password) {
        SecurePreferences preferences =
                new SecurePreferences(context, Constants.PREFERENCES, password, true);
        preferences.put(Constants.PUBLIC_KEY_ID, publicKey); // saves publicKey string in filesystem cyphered using AES (key given above)
    }

    public PublicKey getPublicKey(Context context, String password) throws Exception { // TODO specialized exception

        SecurePreferences preferences =
                new SecurePreferences(context, Constants.PREFERENCES, password, true);
        String publicKeyPEM = preferences.getString(Constants.PUBLIC_KEY_ID);

        publicKeyPEM = publicKeyPEM.replace(Constants.RSA_PUBLIC_BEGIN + '\n', "");
        publicKeyPEM = publicKeyPEM.replace(Constants.RSA_PUBLIC_END, "");
        byte[] encoded = Base64.decode(publicKeyPEM, Base64.DEFAULT);
        KeyFactory kf = KeyFactory.getInstance("RSA");
        return kf.generatePublic(new X509EncodedKeySpec(encoded));
    }

    public String getPublicPemFormat(PublicKey publicKey) {
        String pemPublicKey = Constants.RSA_PUBLIC_BEGIN + '\n';
        pemPublicKey += new String(Base64.encode(publicKey.getEncoded(), Base64.DEFAULT));
        pemPublicKey += Constants.RSA_PUBLIC_END;
        return pemPublicKey;
    }

    // FIXME EXTRACT METHOD
}
