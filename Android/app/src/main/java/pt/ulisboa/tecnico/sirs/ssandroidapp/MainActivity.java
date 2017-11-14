package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

public class MainActivity extends AppCompatActivity {
    private Computer computer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // check if there is a Paired Computer object file
        try {
            ObjectInputStream ois = new ObjectInputStream(this.openFileInput(Constants.COMPUTER_OBJ_FILENAME));
            computer = (Computer) ois.readObject();
            ois.close();
        } catch (IOException ie) {
            // pairing not done yet or filesystem error -> pairing phase needs to be done again
            Toast.makeText(getApplicationContext(), R.string.IOException_read_obj_error_msg, Toast.LENGTH_LONG).show();
        } catch (ClassNotFoundException ce) {
            // unable to get computer obj, pairing needs to be done again
            Toast.makeText(getApplicationContext(), R.string.ClassNotFoundException_error_msg, Toast.LENGTH_LONG).show();
        }


        // running pairing phase always overrides current saved paired computer
        if (savedInstanceState != null) {
            Computer temp = (Computer) savedInstanceState.getSerializable(Constants.COMPUTER_OBJ);
            if (temp != null) computer = temp;
        }

        // shows current paired computer name onscreen if exists
        if (computer != null) {
            TextView tv = findViewById(R.id.statusTV);
            tv.setText( "" + R.string.current_paired_computer_name_msg + computer.getName());
            tv.setVisibility(View.VISIBLE);
        }
    }

    @Override
    public void onPause() {
        super.onPause();
        try {
            ObjectOutputStream oos = new ObjectOutputStream(this.openFileOutput(Constants.COMPUTER_OBJ_FILENAME, this.MODE_PRIVATE));
            oos.writeObject(computer);
            oos.close();
        } catch (IOException ie) {
            Toast.makeText(getApplicationContext(), R.string.IOException_write_obj_error_msg, Toast.LENGTH_LONG).show();
        }
    }

    public void changeActivity2BluetoothPair(View view) {
        Intent intent = new Intent(this, BluetoothActivity.class);
        startActivity(intent);
    }

}
