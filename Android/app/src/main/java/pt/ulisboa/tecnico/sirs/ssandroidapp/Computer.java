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
    private String name = "BANANA"; // bluetooth name FIXME banana

    public void setupPublicKey(String publicKey) {
        try {
            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(Base64.decode(publicKey.trim().getBytes(), Base64.DEFAULT));
            FileOutputStream fos = new FileOutputStream("public.key");
            fos.write(keySpec.getEncoded());
            fos.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getName() { return name; }

    public PublicKey getPublicKey() {
        PublicKey publicKey = null;
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

        return publicKey;
    }
}
