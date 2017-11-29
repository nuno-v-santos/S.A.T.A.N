package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.util.Base64;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
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
    private PublicKey publicKey; // FIXME this is not serializable

    public void setupPublicKey(String pk) throws Exception { // FIXME send specialized exception
        /*X509EncodedKeySpec keySpec = new X509EncodedKeySpec(Base64.decode(pk.trim().getBytes(), Base64.DEFAULT));
        KeyFactory kf = KeyFactory.getInstance("RSA");
        publicKey = kf.generatePublic(keySpec);*/
    }

    public void setName(String name) {
        this.name = name;
    }
    public void setMac(String mac) {
        this.mac = mac;
    }

    public String getName() { return name; }
    public String getMac() { return mac; }

    public PublicKey getPublicKey() {
        return publicKey;
        /*PublicKey publicKey = null;
        try {
            File filePublicKey = new File("public.key");
            FileInputStream fis = new FileInputStream("public.key");
            byte[] encodedPublicKey = new byte[(int) filePublicKey.length()];
            fis.read(encodedPublicKey);
            fis.close();

            KeyFactory keyFactory = KeyFactory.getInstance("RSA");
            X509EncodedKeySpec publicKeySpec = new X509EncodedKeySpec(
                    encodedPublicKey);
            publicKey = keyFactory.generatePublic(publicKeySpec);

        } catch (Exception e) {
            e.printStackTrace();
        }

        return publicKey;*/
    }
}
