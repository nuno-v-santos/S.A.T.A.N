package pt.ulisboa.tecnico.sirs.ssandroidapp.Security;

/**
 * Created by Nuno Santos on 30/11/2017.
 */

public interface EncryptionInterface {

    byte[] encrypt(byte[] message);
    byte[] decrypt(byte[] message);
}
