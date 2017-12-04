package pt.ulisboa.tecnico.sirs.ssandroidapp.Security;

import org.spongycastle.crypto.engines.AESEngine;
import org.spongycastle.crypto.modes.EAXBlockCipher;
import org.spongycastle.crypto.params.AEADParameters;
import org.spongycastle.crypto.params.KeyParameter;

import java.security.Key;
import java.util.Arrays;

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
    public byte[] AESEAXencrypt(byte[] message, Key key, byte[] iv) throws Exception {
        KeyParameter keyParameter = new KeyParameter(key.getEncoded());
        AEADParameters parameters = new AEADParameters(keyParameter, 128, iv, null);

        EAXBlockCipher cipher = new EAXBlockCipher(new AESEngine());
        cipher.init(true, parameters);
        byte[] encrypted = new byte[128];
        int resultLen = cipher.processBytes(message, 0, message.length, encrypted, 0);
        resultLen += cipher.doFinal(encrypted, resultLen); // appends MAC
        return Arrays.copyOfRange(encrypted, 0, resultLen);
    }

    @Override
    public byte[] AESEAXdecrypt(byte[] message, Key key, byte[] iv) throws Exception {
        KeyParameter keyParameter = new KeyParameter(key.getEncoded());
        AEADParameters parameters = new AEADParameters(keyParameter, 128, iv, null);

        EAXBlockCipher cipher = new EAXBlockCipher(new AESEngine());
        cipher.init(false, parameters);
        byte[] decrypted = new byte[128];
        int resultLen = cipher.processBytes(message, 0, message.length, decrypted, 0);
        cipher.doFinal(message, resultLen); // verifies MAC
        return Arrays.copyOfRange(decrypted, 0, resultLen);
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
