package pt.ulisboa.tecnico.sirs.ssandroidapp.Security;

import java.security.Key;

/**
 * Created by Nuno Santos on 30/11/2017.
 */

public interface EncryptionInterface {

    byte[] AESencrypt(byte[] message, Key key, String mode, byte[] iv) throws Exception;
    byte[] AESdecrypt(byte[] message, Key key, String mode, byte[] iv) throws Exception;
    byte[] AESEAXencrypt(byte[] message, Key key, byte[] iv) throws Exception;
    byte[] AESEAXdecrypt(byte[] message, Key key, byte[] iv) throws Exception;
    byte[] RSAencrypt(byte[] message, Key key) throws Exception;
    byte[] RSAdecrypt(byte[] message, Key key) throws Exception;
}
