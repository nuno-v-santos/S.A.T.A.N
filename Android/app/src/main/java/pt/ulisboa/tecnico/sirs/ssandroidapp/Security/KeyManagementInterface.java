package pt.ulisboa.tecnico.sirs.ssandroidapp.Security;

import java.security.Key;
import java.security.KeyPair;

/**
 * Created by Nuno Santos on 30/11/2017.
 */

public interface KeyManagementInterface {
    Key createSymmetricKey(int keySize);
    KeyPair createAssymetricKeys(int keySize);
    Key loadKey(String path);
    void storeKey(Key key, String path);
}
