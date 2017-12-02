package pt.ulisboa.tecnico.sirs.ssandroidapp.Security;

import java.security.Key;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;

/**
 * Created by Nuno Santos on 02/12/2017.
 */

public class Encryption implements EncryptionInterface {

    @Override
    public byte[] AESencrypt(byte[] message, Key key, String mode, byte[] iv) throws Exception {
        Cipher cipher;
        IvParameterSpec ivSpec = new IvParameterSpec(iv);

        cipher = Cipher.getInstance("AES/" + mode + "/PKCS7Padding");
        cipher.init(Cipher.ENCRYPT_MODE, key, ivSpec);
        return cipher.doFinal(message);
    }

    @Override
    public byte[] AESdecrypt(byte[] message, Key key, String mode, byte[] iv) throws Exception {
        Cipher cipher;
        IvParameterSpec ivSpec = new IvParameterSpec(iv);

        cipher = Cipher.getInstance("AES/" + mode + "/PKCS7Padding");
        cipher.init(Cipher.DECRYPT_MODE, key, ivSpec);
        return cipher.doFinal(message);
    }

    @Override
    public byte[] RSAencrypt(byte[] message, Key key) throws Exception {
        Cipher cipher = Cipher.getInstance("RSA/NONE/OAEPWithSHA-256AndMGF1Padding");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        return cipher.doFinal(message);
    }

    @Override
    public byte[] RSAdecrypt(byte[] message, Key key) throws Exception {
        Cipher cipher = Cipher.getInstance("RSA/NONE/OAEPWithSHA-256AndMGF1Padding");
        cipher.init(Cipher.DECRYPT_MODE, key);
        return cipher.doFinal(message);
    }
}
