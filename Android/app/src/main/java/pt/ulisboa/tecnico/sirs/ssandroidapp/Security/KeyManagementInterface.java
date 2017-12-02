package pt.ulisboa.tecnico.sirs.ssandroidapp.Security;

import android.content.Context;

import java.security.InvalidAlgorithmParameterException;
import java.security.Key;
import java.security.KeyPair;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.spec.InvalidKeySpecException;

/**
 * Created by Nuno Santos on 30/11/2017.
 */

public interface KeyManagementInterface {
    Key createSymmetricKey(int keySize) throws NoSuchAlgorithmException;
    Key createSymmetricKey(byte[] encodedKey) throws NoSuchAlgorithmException;
    KeyPair createAssymetricKeys(int keySize) throws NoSuchAlgorithmException, InvalidAlgorithmParameterException;
    Key loadKey(Context context, String id, String password) throws NoSuchAlgorithmException, InvalidKeySpecException;
    void storeKey(Context context, Key key, String id, String password);
    String getKeyPEMFormat(PublicKey key);
    PublicKey generatePublicKeyFromPEM(String publicKeyPEM) throws NoSuchAlgorithmException, InvalidKeySpecException;
}
