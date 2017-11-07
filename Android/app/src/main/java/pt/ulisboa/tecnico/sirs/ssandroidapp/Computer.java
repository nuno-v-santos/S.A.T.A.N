package pt.ulisboa.tecnico.sirs.ssandroidapp;

/**
 * Created by Guilherme on 07/11/2017.
 */

public class Computer {
    private String id;
    private String publicKey; // FIXME STRING?

    public Computer(String id, String publicKey) {
        this.id = id;
        this.publicKey = publicKey;
    }

    public String getId() {
        return id;
    }

    public String getPublicKey() {
        return publicKey;
    }
}
