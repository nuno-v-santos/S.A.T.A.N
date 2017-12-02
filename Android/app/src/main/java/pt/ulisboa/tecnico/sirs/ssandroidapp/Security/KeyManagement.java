package pt.ulisboa.tecnico.sirs.ssandroidapp.Security;

import android.content.Context;
import android.util.Base64;

import java.security.InvalidAlgorithmParameterException;
import java.security.Key;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.RSAKeyGenParameterSpec;
import java.security.spec.X509EncodedKeySpec;

import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

import pt.ulisboa.tecnico.sirs.ssandroidapp.Constants;

/**
 * Created by Guilherme on 01/12/2017.
 */

public class KeyManagement implements KeyManagementInterface {

    @Override
    public Key createSymmetricKey(int keySize) throws NoSuchAlgorithmException {
        KeyGenerator keyGen = KeyGenerator.getInstance("AES");
        keyGen.init(keySize);
        SecretKey secretKey = keyGen.generateKey();
        return secretKey;
    }

    @Override
    public Key createSymmetricKey(byte[] encodedKey) throws NoSuchAlgorithmException {
        return new SecretKeySpec(encodedKey, "AES");
    }

    @Override
    public KeyPair createAssymetricKeys(int keySize) throws NoSuchAlgorithmException, InvalidAlgorithmParameterException {
        RSAKeyGenParameterSpec spec = new RSAKeyGenParameterSpec(keySize, RSAKeyGenParameterSpec.F4);
        KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");
        keyGen.initialize(spec);
        KeyPair keyPair = keyGen.generateKeyPair();
        return keyPair;
    }

    @Override
    public Key loadKey(Context context, String id, String password) throws NoSuchAlgorithmException, InvalidKeySpecException {
        SecurePreferences preferences =
                new SecurePreferences(context, Constants.PREFERENCES, password, true);
        String base64Key = preferences.getString(id);

        String[] lines = base64Key.split("\\r?\\n");

        Key key;
        if (lines[0].equals(Constants.RSA_PUBLIC_BEGIN)) {                  // Public RSA key load
            base64Key = base64Key.replace(Constants.RSA_PUBLIC_BEGIN + '\n', "");
            byte[] encoded = Base64.decode(base64Key, Base64.DEFAULT);
            KeyFactory kf = KeyFactory.getInstance("RSA");
            key = kf.generatePublic(new X509EncodedKeySpec(encoded));

        } else if (lines[0].equals(Constants.RSA_PRIVATE_BEGIN)) {          // Private RSA key load
            base64Key = base64Key.replace(Constants.RSA_PRIVATE_BEGIN + '\n', "");
            byte[] encoded = Base64.decode(base64Key, Base64.DEFAULT);
            KeyFactory kf = KeyFactory.getInstance("RSA");
            key = kf.generatePrivate(new PKCS8EncodedKeySpec(encoded));
        } else {                                                            // AES key load
            base64Key = base64Key.replace(Constants.AES_BEGIN + '\n', "");
            byte[] encoded = Base64.decode(base64Key, Base64.DEFAULT);
            key = new SecretKeySpec(encoded, "AES");
        }
        return key;
    }

    /**
     * Stores key in Android Filesystem encrypted with a user given password using AES
     * @param context Activity context that wants to store the key
     * @param key   Key to be stored
     * @param id    Identification referencing the stored key
     * @param password Password used to cypher the key when stored
     */
    @Override
    public void storeKey(Context context, Key key, String id, String password) {
        SecurePreferences preferences =
                new SecurePreferences(context, Constants.PREFERENCES, password, true);

        String begin;

        switch (key.getAlgorithm()) {
            case ("RSA") :
                if (key.getFormat().equals("X.509")) // public
                    begin = Constants.RSA_PUBLIC_BEGIN + "\n";
                else begin = Constants.RSA_PRIVATE_BEGIN + "\n";
                break;
            case ("AES") :
                begin = Constants.AES_BEGIN + "\n";
                break;
            default :
                throw new UnsupportedOperationException();
        }

        String base64Key = begin + Base64.encodeToString(key.getEncoded(), Base64.DEFAULT);

        preferences.put(id, base64Key);
    }

    @Override
    public String getKeyPEMFormat(PublicKey key) {
        String begin = Constants.RSA_PUBLIC_BEGIN + "\n";
        String end = Constants.RSA_PUBLIC_END;

        String PEMKey = begin + Base64.encodeToString(key.getEncoded(), Base64.DEFAULT) + end;

        return PEMKey;
    }

    @Override
    public PublicKey generatePublicKeyFromPEM(String publicKeyPEM) throws NoSuchAlgorithmException, InvalidKeySpecException {
        publicKeyPEM = publicKeyPEM.replace(Constants.RSA_PUBLIC_BEGIN + '\n', "");
        publicKeyPEM = publicKeyPEM.replace(Constants.RSA_PUBLIC_END, "");
        byte[] encoded = Base64.decode(publicKeyPEM, Base64.DEFAULT);
        KeyFactory kf = KeyFactory.getInstance("RSA");
        return kf.generatePublic(new X509EncodedKeySpec(encoded));
    }

    @Override
    public byte[] loadIV(Context context, String id, String password) {
        SecurePreferences preferences =
                new SecurePreferences(context, Constants.PREFERENCES, password, true);
        String base64IV = preferences.getString(id);
        byte[] iv = Base64.decode(base64IV, Base64.DEFAULT);
        return iv;
    }

    @Override
    public void storeIV(Context context, byte[] iv, String id, String password) {
        SecurePreferences preferences =
                new SecurePreferences(context, Constants.PREFERENCES, password, true);
        String base64IV = Base64.encodeToString(iv, Base64.DEFAULT);
        preferences.put(Constants.ANDROID_MEK_IV_ID, base64IV);
    }
}
